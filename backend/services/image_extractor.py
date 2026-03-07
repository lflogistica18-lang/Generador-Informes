"""
image_extractor.py — Extracción de imágenes de desvíos fotográficos de PDFs Conforme

Usa PyMuPDF para extraer imágenes embebidas de las páginas de relevamientos.
Las guarda en disco y retorna rutas + base64 para el frontend.
"""
import fitz
import base64
import os
import re
from typing import List
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import DesvioFotografico


UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def _clasificar_tipo_plaga(sector: str, descripcion: str) -> str:
    """
    Clasifica el tipo de plaga del desvío basándose en el contexto textual.
    Retorna: 'roedores' | 'voladores' | 'rastreros' | 'otros'
    """
    texto = f"{sector or ''} {descripcion or ''}".lower()
    
    # Prioridad: Voladores (TUV suele ser muy específico)
    if any(k in texto for k in ["mosca", "volador", "trampa uv", "tuv", "insectocut", "polilla", "lepidoptero", "mosquito"]):
        return "voladores"
    # Rastreros
    elif any(k in texto for k in ["cucaracha", "rastrero", "hormiga", "insecto", "aracnido", "araña", "blatella"]):
        return "rastreros"
    # Roedores (palabras clave muy específicas para no capturar falsos positivos)
    elif any(k in texto for k in ["roedor", "rata", "raton", "cebadera", "cb", "placa de pegamento", "consumo", "rodenticida"]):
        return "roedores"
    # Aves / Otros / Estructural
    elif any(k in texto for k in ["paloma", "ave", "pajaro", "nido", "pincho", "malla", "estructural", "cerramiento", "abertura"]):
        return "otros"
    
    # Por defecto, si no hay pista clara → otros (más seguro para no sesgar roedores)
    return "otros"


def extraer_imagenes_conforme(filepath: str, track_id: str = "unknown") -> List[DesvioFotografico]:
    """
    Extrae las imágenes de desvíos fotográficos de un PDF Conforme.
    
    Solo extrae imágenes de las páginas de RELEVAMIENTOS (pág 3 en adelante).
    Ignora logos, firmas y otros elementos gráficos de páginas 1-2.
    
    Retorna lista de DesvioFotografico con rutas a las imágenes guardadas.
    """
    desvios = []
    
    try:
        doc = fitz.open(filepath)
        
        # Crear directorio de salida para imágenes de esta visita
        img_dir = os.path.join(UPLOADS_DIR, "images", f"conforme_{track_id}")
        os.makedirs(img_dir, exist_ok=True)
        
        # Set para evitar duplicados (mismo XRef usado en varias páginas, ej: logos)
        seen_xrefs = set()
        
        # Páginas de relevamientos (skip primeras 2 págs)
        for num_pag in range(2, len(doc)):
            pagina = doc[num_pag]
            texto_pag = pagina.get_text()
            
            # Extraer contexto de la página (sector y descripción)
            sector = None
            descripcion = None
            
            sector_match = re.search(r"Sector:\s*([^\n]+)", texto_pag)
            if sector_match:
                sector = sector_match.group(1).strip()
            
            # Buscar descripción en el texto de la página
            lineas = [l.strip() for l in texto_pag.split('\n') if l.strip()]
            desc_partes = []
            for i, linea in enumerate(lineas):
                lin_low = linea.lower()
                # Filtro robusto para URLs y texto basura
                if "sanitas" in lin_low or "ambiental" in lin_low or \
                   linea in ["RELEVAMIENTOS", "Avistamiento"] or \
                   linea.isdigit():
                    continue
                if sector and sector in linea:
                    continue
                if "Sector:" in linea:
                    continue
                desc_partes.append(linea)
                if len(desc_partes) >= 2:
                    break
            
            descripcion = " - ".join(desc_partes)
            if len(descripcion) > 100:
                descripcion = descripcion[:97] + "..."
            
            tipo_plaga = _clasificar_tipo_plaga(sector or "", descripcion or "")
            
            # Extraer imágenes de la página
            imagenes = pagina.get_images(full=True)
            
            for img_idx, img_info in enumerate(imagenes):
                xref = img_info[0]
                
                # Evitar duplicados (logos repetidos en header/footer)
                if xref in seen_xrefs:
                    continue
                
                try:
                    base_image = doc.extract_image(xref)
                    img_bytes = base_image["image"]
                    img_ext = base_image["ext"]
                    width = base_image["width"]
                    height = base_image["height"]
                    
                    # FILTRADO MEJORADO
                    # Criterio 1: Tamaño en bytes (Aumentado a 45KB para filtrar fotos de perfil/firmas de alta calidad)
                    if len(img_bytes) < 45000:
                        continue
                        
                    # Criterio 2: Dimensiones (Aumentado a 200px)
                    if width < 200 or height < 200:
                        continue
                        
                    # Criterio 3: Relación de aspecto extrema (firmas suelen ser anchas y bajas)
                    aspect_ratio = width / height
                    if aspect_ratio > 3.0 or aspect_ratio < 0.3:
                        continue
                    
                    # Si pasa los filtros, lo marcamos como visto
                    seen_xrefs.add(xref)

                    # Guardar imagen en disco
                    img_filename = f"pag{num_pag}_img{img_idx}.{img_ext}"
                    img_path = os.path.join(img_dir, img_filename)
                    
                    with open(img_path, "wb") as f:
                        f.write(img_bytes)
                    
                    # Convertir a base64 para el frontend
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    
                    desvio = DesvioFotografico(
                        sector=sector,
                        descripcion=descripcion,
                        tipo_plaga=tipo_plaga,
                        imagen_path=img_path,
                        imagen_base64=f"data:image/{img_ext};base64,{img_b64}",
                    )
                    desvios.append(desvio)
                    
                    # En una página de relevamiento, suele haber una foto principal
                    # Si ya encontramos una imagen grande, hay que seguir buscando las demás
                    
                except Exception as img_err:
                    print(f"Error extrayendo imagen {img_idx} en pág {num_pag}: {img_err}")
                    continue
        
        doc.close()
        
    except Exception as e:
        print(f"Error extrayendo imágenes de {filepath}: {e}")
    
    return desvios
