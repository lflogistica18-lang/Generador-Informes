"""
upload.py — Router de FastAPI para carga y parseo de PDFs
"""
import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from models.schemas import UploadResponse, ParsedConforme, ParsedMIP
from services.pdf_parser_conforme import parsear_conforme, es_conforme
from services.pdf_parser_mip import parsear_mip, es_mip
from services.image_extractor import extraer_imagenes_conforme

router = APIRouter()

# Directorio de subidas (Ruta absoluta segura)
UPLOADS_DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(UPLOADS_DIR_BASE, "uploads")
IMAGES_DIR = os.path.join(UPLOADS_DIR, "images")


@router.post("/", response_model=UploadResponse)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Recibe múltiples PDFs, los clasifica (Conforme vs MIP) y parsea.
    Retorna los datos extraídos + lista de campos faltantes.
    """
    print(f"--- NUEVA PETICIÓN DE SUBIDA: {len(files)} archivos ---")
    print(f"UPLOADS_DIR actual: {UPLOADS_DIR}")
    
    # Asegurar que el directorio de uploads exista
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    conformes: List[ParsedConforme] = []
    mips: List[ParsedMIP] = []
    errores: List[str] = []
    campos_faltantes: List[dict] = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            errores.append(f"{file.filename}: No es un archivo PDF")
            continue

        # Guardar temporalmente
        file_id = str(uuid.uuid4())[:8]
        temp_path = os.path.join(UPLOADS_DIR, f"{file_id}_{file.filename}")

        try:
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # Debug: Ver qué tiene el PDF
            import fitz
            doc = fitz.open(temp_path)
            texto_debug = doc[0].get_text()[:200] if len(doc) > 0 else "VACÍO"
            doc.close()
            print(f"--- Procesando: {file.filename} ---")
            print(f"Texto inicio: {texto_debug!r}")

            # Detectar tipo y parsear
            if es_mip(temp_path):
                print(">> Detectado como MIP")
                mip = parsear_mip(temp_path)
                mips.append(mip)

            elif es_conforme(temp_path):
                print(">> Detectado como Conforme")
                conforme = parsear_conforme(temp_path)
                # Extraer imágenes de desvíos
                imagenes = extraer_imagenes_conforme(temp_path, conforme.track_id or file_id)
                if imagenes:
                    conforme.desvios = imagenes
                conformes.append(conforme)

                
                if conforme.campos_faltantes:
                    campos_faltantes.append({
                        "archivo": file.filename,
                        "fecha": conforme.fecha or "desconocida",
                        "campos": conforme.campos_faltantes,
                    })

            else:
                print(">> NO DETECTADO (Ni MIP ni Conforme)")
                errores.append(f"{file.filename}: No se pudo identificar el tipo (ni Conforme ni MIP). Texto inicio: {texto_debug[:50]}...")

        except Exception as e:
            print(f"Error procesando {file.filename}: {e}")
            errores.append(f"{file.filename}: Error al procesar — {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            continue

    return UploadResponse(
        archivos_procesados=len(conformes) + len(mips),
        conformes=conformes,
        mips=mips,
        errores=errores,
        campos_faltantes=campos_faltantes,
    )
