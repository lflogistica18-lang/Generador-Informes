"""
pdf_parser_conforme.py — Parseo de PDFs tipo "Conforme" (Informe de Visita)

Estrategia: extracción de texto con PyMuPDF + regex por secciones.
Los PDFs Conforme tienen estructura consistente con labels tipo "Tipo:", "Modo:", etc.
"""
import re
import fitz  # PyMuPDF
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import (
    ParsedConforme, ServicioRastreros, ServicioVoladores,
    ServicioRoedores, ReceptorServicio, DesvioFotografico
)
from typing import Any


def _parse_float(valor: Any) -> Optional[float]:
    """
    Parsea un valor string a float, limpiando unidades como 'gr'.
    Regla de negocio: Si no se especifica 'gr' u otra unidad, se asume que
    el valor son UNIDADES y se multiplica por 10 (1 unidad = 10 gr).
    """
    if not valor:
        return None
    s = str(valor).lower().strip()
    
    # Detectar si ya tiene unidad de gramos explícitamente
    tiene_unidad = "gr" in s or " g" in s or s.endswith("g")
    
    # Limpiar string para convertir a float
    s = s.replace("gr", "").replace("g", "").replace(",", ".").strip()
    
    try:
        val = float(s)
        # Si NO tiene unidad explícita, aplicamos el factor x10 (unidades -> gramos)
        if not tiene_unidad:
            return val * 10
        return val
    except ValueError:
        return None


def _limpiar_branding_y_basura(texto: Optional[str]) -> Optional[str]:
    """Limpia URLs de Sanitas, números de página y basura del texto."""
    if not texto:
        return None
    # Eliminar URL de Sanitas y basura del pie de página
    texto = re.sub(r"www\.sanitasambiental\.com\.ar.*", "", texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r"sanitasambiental", "", texto, flags=re.IGNORECASE)
    # Eliminar números de página sueltos al final de líneas
    texto = re.sub(r"\s+\d+\s*$", "", texto)
    # Limpiar saltos de línea y normalizar espacios
    texto = re.sub(r'\n', ' ', texto)
    return texto.strip()


def _extraer_valor(texto: str, label: str) -> Optional[str]:
    """Extrae el valor que sigue a un label en el texto. Ej: 'Modo:\nPreventiva' → 'Preventiva'"""
    # Usar el _limpiar_texto existente para encoding y luego el de branding
    patron = rf"{re.escape(label)}\s*\n?\s*(.+?)(?=\n[A-ZÁÉÍÓÚÜ][a-záéíóúü]+:|$)"
    match = re.search(patron, texto, re.DOTALL)
    if match:
        return _limpiar_branding_y_basura(_limpiar_texto(match.group(1)))
    return None


def _extraer_valor_simple(texto: str, label: str) -> Optional[str]:
    """Extrae solo la primera línea después del label."""
    patron = rf"{re.escape(label)}\s*\n?\s*([^\n]+)"
    match = re.search(patron, texto)
    if match:
        return _limpiar_branding_y_basura(_limpiar_texto(match.group(1)))
    return None


def _limpiar_texto(texto: str) -> str:
    """Normaliza encoding y limpia caracteres extraños del texto extraído."""
    # Reemplazar variantes de tildes y ñ mal encoded
    reemplazos = {
        '├│': 'o', '├¡': 'i', '├║': 'u', '├▒': 'ñ',
        '├ü': 'A', '├Á': 'A', '├®': 'e', '├¬': 'e',
        '┬¡': '!', '┬¬': '¬', '┬®': '©', '─░': 'z',
        '├ô': 'O', 'ì': 'i', 'ú': 'u',
    }
    for mal, bien in reemplazos.items():
        texto = texto.replace(mal, bien)
    return texto


def _parse_bloque_servicio(bloque: str, tipo_servicio: str) -> dict:
    """Parsea un bloque de servicio individual. Retorna dict con los campos."""
    datos = {}

    # Modo
    modo = _extraer_valor_simple(bloque, "Modo:")
    if modo:
        datos["modo"] = modo

    # Avistamiento
    avist = _extraer_valor_simple(bloque, "Avistamiento:")
    if avist:
        datos["avistamiento"] = avist

    if "Rastreros" in tipo_servicio:
        datos["maquinarias"] = _extraer_valor_simple(bloque, "Maquinarias:")
        datos["producto"] = _extraer_valor_simple(bloque, "Producto:")
        # Comentarios multilínea
        comentarios = _extraer_valor(bloque, "Comentarios:")
        datos["comentarios"] = comentarios

    # Voladores / Mosquitos
    elif "Mosquitos" in tipo_servicio or "Voladores" in tipo_servicio:
        datos["producto"] = _extraer_valor_simple(bloque, "Producto:")
        
        # Captura mejorada para comentarios multilínea
        match_com = re.search(r"Comentarios:\s*\n?(.+)", bloque, re.DOTALL)
        if match_com:
            datos["comentarios"] = _limpiar_branding_y_basura(_limpiar_texto(match_com.group(1)))
        else:
            datos["comentarios"] = None

    # Roedores / Desratización
    elif "Desratizaci" in tipo_servicio or "Roedor" in tipo_servicio:
        consumo = _extraer_valor_simple(bloque, "Consumo:")
        datos["consumo"] = _parse_float(consumo)
        avist_n = _extraer_valor_simple(bloque, "Avistamiento:")
        datos["avistamiento"] = int(avist_n) if avist_n and avist_n.isdigit() else avist_n
        repos = _extraer_valor_simple(bloque, "Reposici")
        datos["reposicion"] = int(repos) if repos and repos.isdigit() else None
        capturas = _extraer_valor_simple(bloque, "Capturas:")
        datos["capturas"] = int(capturas) if capturas and capturas.isdigit() else None
        obs = _extraer_valor(bloque, "Observaciones:")
        datos["observaciones"] = obs

    return datos


def _detectar_campos_faltantes_conforme(conforme: ParsedConforme) -> list:
    """Detecta qué campos obligatorios están ausentes y retorna lista de descripciones."""
    faltantes = []

    if not conforme.fecha:
        faltantes.append("Fecha de visita")
    if not conforme.operario:
        faltantes.append("Nombre del operario")

    # Rastreros
    r = conforme.rastreros
    if r and r.modo and r.modo.lower() != "no realizado":
        if not r.producto:
            faltantes.append("Rastreros: Producto")
        if not r.comentarios:
            faltantes.append("Rastreros: Comentarios / Sectores tratados")

    # Voladores
    v = conforme.voladores
    if v and v.modo and v.modo.lower() != "no realizado":
        if not v.producto:
            faltantes.append("Voladores: Producto (placas UV)")
        if not v.comentarios:
            faltantes.append("Voladores: Comentarios")

    return faltantes


def parsear_conforme(filepath: str) -> ParsedConforme:
    """
    Parsea un PDF Conforme y retorna un objeto ParsedConforme.
    
    Estructura del PDF:
    - Pág 1: Encabezado, servicios, datos operario (al final)
    - Pág 2: Conforme de servicio (receptor)
    - Págs 3+: Relevamientos fotográficos (si hay desvíos)
    """
    conforme = ParsedConforme()
    doc = fitz.open(filepath)
    
    # ── Página 1: Encabezado + Servicios ──────────────────────────────────────
    if len(doc) < 1:
        doc.close()
        return conforme

    pagina1_texto = doc[0].get_text()
    texto_completo = pagina1_texto

    # Encabezado
    track_match = re.search(r"TRACK ID #(\d+)", texto_completo)
    if track_match:
        conforme.track_id = track_match.group(1)

    # Cliente y dirección (líneas antes del INFORME CONTROL DE PLAGAS)
    lineas = texto_completo.split('\n')
    lineas = [l.strip() for l in lineas if l.strip()]
    
    for i, linea in enumerate(lineas):
        if "SANITAS AMBIENTAL" in linea:
            # El cliente suele estar 3-4 líneas después
            for j in range(i + 1, min(i + 8, len(lineas))):
                if "INFORME CONTROL" in lineas[j] or "Empresa Certificada" in lineas[j]:
                    break
                if "CALSA" in lineas[j] or ("Planta" in lineas[j]) or (lineas[j] and not lineas[j][0].isdigit()):
                    if not conforme.cliente and "ISO" not in lineas[j]:
                        conforme.cliente = lineas[j]
                    elif not conforme.direccion and "Av." in lineas[j]:
                        conforme.direccion = lineas[j]

    # Datos del operario (aparecen al final de la pág 1, antes del link www.)
    fecha_match = re.search(r"Fecha:\s*(\d{2}/\d{2}/\d{4})", texto_completo)
    if fecha_match:
        conforme.fecha = fecha_match.group(1)

    nombre_operario = re.search(r"Nombre:\s*([^\n]+)\s*\n", texto_completo)
    if nombre_operario:
        conforme.operario = nombre_operario.group(1).strip()

    ingreso_match = re.search(r"Ingreso:\s*(\d{2}:\d{2})", texto_completo)
    if ingreso_match:
        conforme.ingreso = ingreso_match.group(1)

    egreso_match = re.search(r"Egreso:\s*(\d{2}:\d{2})", texto_completo)
    if egreso_match:
        conforme.egreso = egreso_match.group(1)

    # ── Parseo de bloques de servicio ─────────────────────────────────────────
    # Los servicios están separados por bloques que empiezan con "Tipo:"
    # Dividimos por "Tipo:" para obtener cada bloque
    bloques = re.split(r'\nTipo:\s*\n', texto_completo)
    
    for bloque in bloques[1:]:  # primer bloque es el encabezado
        # Determinar qué tipo de servicio es
        tipo_linea_match = re.match(r'([^\n]+)', bloque)
        if not tipo_linea_match:
            continue
        tipo_servicio = tipo_linea_match.group(1).strip()
        
        datos = _parse_bloque_servicio(bloque, tipo_servicio)
        
        if "Rastreros" in tipo_servicio:
            conforme.rastreros = ServicioRastreros(
                modo=datos.get("modo"),
                maquinarias=datos.get("maquinarias"),
                producto=datos.get("producto"),
                avistamiento=datos.get("avistamiento"),
                comentarios=datos.get("comentarios"),
            )
        elif "Mosquitos" in tipo_servicio:
            conforme.voladores = ServicioVoladores(
                modo=datos.get("modo"),
                producto=datos.get("producto"),
                avistamiento=datos.get("avistamiento"),
                comentarios=datos.get("comentarios"),
            )
        elif "Desratizaci" in tipo_servicio:
            conforme.roedores = ServicioRoedores(
                modo=datos.get("modo"),
                consumo=datos.get("consumo"),
                avistamiento=datos.get("avistamiento"),
                reposicion=datos.get("reposicion"),
                capturas=datos.get("capturas"),
                observaciones=datos.get("observaciones"),
            )

    # ── Página 2: Conforme de servicio (receptor) ─────────────────────────────
    if len(doc) >= 2:
        pag2_texto = doc[1].get_text()
        receptor = ReceptorServicio()
        
        nombre_rec = re.search(r"Nombre:\s*([^\n]+)", pag2_texto)
        if nombre_rec:
            receptor.nombre = nombre_rec.group(1).strip()
        
        apellido_rec = re.search(r"Apellido:\s*([^\n]+)", pag2_texto)
        if apellido_rec:
            receptor.apellido = apellido_rec.group(1).strip()
        
        dni_rec = re.search(r"Dni:\s*([^\n]+)", pag2_texto)
        if dni_rec:
            receptor.dni = dni_rec.group(1).strip()
        
        puesto_rec = re.search(r"Puesto:\s*([^\n]+)", pag2_texto)
        if puesto_rec:
            receptor.puesto = puesto_rec.group(1).strip()
        
        conforme.receptor = receptor

    # ── Páginas 3+: Relevamientos fotográficos ────────────────────────────────
    from .image_extractor import _clasificar_tipo_plaga
    
    for num_pag in range(2, len(doc)):
        pagina = doc[num_pag]
        texto_pag = pagina.get_text()
        
        if "RELEVAMIENTOS" in texto_pag or "Avistamiento" in texto_pag:
            # Extraer sector y descripción del texto
            sector_match = re.search(r"Sector:\s*([^\n]+)", texto_pag)
            sector = sector_match.group(1).strip() if sector_match else None
            
            # Búsqueda robusta de descripción (misma lógica que image_extractor)
            lineas_pag = [l.strip() for l in texto_pag.split('\n') if l.strip()]
            desc_partes = []
            for i, linea in enumerate(lineas_pag):
                lin_low = linea.lower()
                if "sanitas" in lin_low or "ambiental" in lin_low or \
                   linea in ["RELEVAMIENTOS", "Avistamiento"] or \
                   linea.isdigit():
                    continue
                if sector and sector in linea:
                    continue
                if "Sector:" in linea:
                    continue
                desc_partes.append(linea)
                if len(desc_partes) >= 2: # Solo tomar las primeras dos líneas útiles para evitar ruido extra
                    break
            
            descripcion = " - ".join(desc_partes)
            if len(descripcion) > 100:
                descripcion = descripcion[:97] + "..."
            
            tipo_plaga = _clasificar_tipo_plaga(sector or "", descripcion or "")
            
            desvio = DesvioFotografico(
                sector=sector,
                descripcion=descripcion,
                tipo_plaga=tipo_plaga,
            )
            conforme.desvios.append(desvio)

    # ── Detectar campos faltantes ──────────────────────────────────────────────
    conforme.campos_faltantes = _detectar_campos_faltantes_conforme(conforme)

    doc.close()
    return conforme


def es_conforme(filepath: str) -> bool:
    """Detecta si un PDF es de tipo Conforme (vs MIP)."""
    try:
        doc = fitz.open(filepath)
        texto = doc[0].get_text() if len(doc) > 0 else ""
        doc.close()
        return "INFORME CONTROL DE PLAGAS" in texto or "TRACK ID" in texto
    except Exception:
        return False
