"""
pdf_parser_mip.py — Parseo de PDFs tipo "MIP" (Registro de Roedores)

Estrategia:
- Página 1: regex para extraer dashboard resumen + productos
- Páginas 2-3: pdfplumber para tablas de consumos, capturas, reposiciones
- Páginas 4-6: pdfplumber para la tabla de relevamiento original (punto por punto)
- Página 7: firma de conformidad
"""
import re
import pdfplumber
import fitz
from typing import Optional, List, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import (
    ParsedMIP, DashboardMIP, RegistroConsumo,
    RegistroReposicion, RegistroCaptura, PuntoRelevamiento
)


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


def _parse_dashboard(texto_pag1: str) -> DashboardMIP:
    """Extrae el dashboard resumen de la página 1 del PDF MIP."""
    dashboard = DashboardMIP()

    # CONSUMOS → número → gramos totales
    consumos_match = re.search(r"CONSUMOS\s*\n(\d+)\s*\n([\d.]+)\s*gr", texto_pag1, re.IGNORECASE)
    if consumos_match:
        dashboard.total_consumos = int(consumos_match.group(1))
        dashboard.gramos_consumos = float(consumos_match.group(2))
    else:
        # Fallback: solo el número
        consumos_n = re.search(r"CONSUMOS\s*\n?(\d+)", texto_pag1)
        if consumos_n:
            dashboard.total_consumos = int(consumos_n.group(1))
        gramos_match = re.search(r"([\d.]+)\s*gr totales", texto_pag1)
        if gramos_match:
            dashboard.gramos_consumos = float(gramos_match.group(1))

    # CAPTURAS
    capturas_match = re.search(r"CAPTURAS\s*\n?(\d+)", texto_pag1)
    if capturas_match:
        dashboard.total_capturas = int(capturas_match.group(1))

    # REPOSICIONES → número → "Cebos: X gr | Placas: Y un"
    repos_match = re.search(r"REPOSICIONES\s*\n?(\d+)", texto_pag1)
    if repos_match:
        dashboard.total_reposiciones = int(repos_match.group(1))

    cebos_repos = re.search(r"Cebos:\s*([\d.]+)\s*gr", texto_pag1)
    if cebos_repos:
        dashboard.gramos_reposiciones = float(cebos_repos.group(1))

    placas_repos = re.search(r"Placas:\s*(\d+)\s*un", texto_pag1)
    if placas_repos:
        dashboard.placas_reposicion = int(placas_repos.group(1))

    # OPERARIOS
    operarios_match = re.search(r"OPERARIOS\s*\n?(\d+)", texto_pag1)
    if operarios_match:
        dashboard.total_operarios = int(operarios_match.group(1))

    return dashboard


def _parse_productos(texto_pag1: str) -> List[str]:
    """Extrae la lista de productos de la página 1."""
    productos = []
    
    # Los productos van después de "Productos Utilizados" y antes de "Comentarios"
    match = re.search(r"Productos Utilizados\s*\n(.*?)(?:Comentarios|$)", texto_pag1, re.DOTALL)
    if match:
        bloque = match.group(1).strip()
        for linea in bloque.split('\n'):
            linea = linea.strip()
            if linea and linea not in ['', ' ']:
                productos.append(linea)
    
    return productos


def _limpiar_filas_tabla(filas: List[List]) -> List[List]:
    """
    Las tablas de pdfplumber tienen filas duplicadas con None.
    Filtra las filas que tienen todos los campos críticos en None.
    También hace forward-fill de la subsección.
    """
    filas_limpias = []
    subseccion_actual = None
    
    for fila in filas:
        if fila is None:
            continue
        
        # Detectar si es fila de datos reales (al menos 3 campos no-None)
        no_none = sum(1 for c in fila if c is not None)
        if no_none < 2:
            continue
        
        # Forward-fill de subsección (primera columna)
        if fila[0] is not None and str(fila[0]).strip():
            subseccion_actual = str(fila[0]).strip()
        
        fila_lista = list(fila)
        if subseccion_actual and (fila_lista[0] is None or not str(fila_lista[0]).strip()):
            fila_lista[0] = subseccion_actual
        
        filas_limpias.append(fila_lista)
    
    return filas_limpias


def _parse_tabla_consumos(pdf_plumber, num_pag: int) -> List[RegistroConsumo]:
    """Parsea la tabla de consumos de la página dada."""
    consumos = []
    
    page = pdf_plumber.pages[num_pag]
    tables = page.extract_tables()
    
    for tabla in tables:
        if not tabla or len(tabla) < 2:
            continue
        
        # Verificar header
        header = [str(h).upper() if h else '' for h in tabla[0]]
        if "PUNTO CONTROL" not in ' '.join(header) and "PUNTO" not in ' '.join(header):
            continue
        
        for fila in tabla[1:]:
            if not fila or sum(1 for c in fila if c is not None) < 3:
                continue
            
            try:
                consumo = RegistroConsumo(
                    id=str(fila[0]).strip() if fila[0] else None,
                    operario=str(fila[1]).strip() if len(fila) > 1 and fila[1] else None,
                    insumo=str(fila[2]).strip() if len(fila) > 2 and fila[2] else None,
                    punto_control=str(fila[3]).strip() if len(fila) > 3 and fila[3] else None,
                    cantidad=_parse_float(fila[4]) if len(fila) > 4 else None,
                    fecha=str(fila[5]).strip() if len(fila) > 5 and fila[5] else None,
                    comentario=str(fila[6]).strip() if len(fila) > 6 and fila[6] else None,
                )
                consumos.append(consumo)
            except (ValueError, IndexError):
                continue
    
    return consumos


def _parse_tabla_reposiciones(pdf_plumber, num_pag: int) -> List[RegistroReposicion]:
    """Parsea la tabla de reposiciones."""
    reposiciones = []
    
    page = pdf_plumber.pages[num_pag]
    tables = page.extract_tables()
    
    for tabla in tables:
        if not tabla or len(tabla) < 2:
            continue
        
        header = [str(h).upper() if h else '' for h in tabla[0]]
        if "TIPO" not in ' '.join(header):
            continue
        
        for fila in tabla[1:]:
            if not fila or sum(1 for c in fila if c is not None) < 3:
                continue
            
            try:
                repos = RegistroReposicion(
                    id=str(fila[0]).strip() if fila[0] else None,
                    operario=str(fila[1]).strip() if len(fila) > 1 and fila[1] else None,
                    insumo=str(fila[2]).strip() if len(fila) > 2 and fila[2] else None,
                    tipo=str(fila[3]).strip() if len(fila) > 3 and fila[3] else None,
                    punto_control=str(fila[4]).strip() if len(fila) > 4 and fila[4] else None,
                    cantidad=int(str(fila[5]).strip()) if len(fila) > 5 and fila[5] and str(fila[5]).strip().isdigit() else None,
                    fecha=str(fila[6]).strip() if len(fila) > 6 and fila[6] else None,
                    comentario=str(fila[7]).strip() if len(fila) > 7 and fila[7] else None,
                )
                reposiciones.append(repos)
            except (ValueError, IndexError):
                continue
    
    return reposiciones


def _parse_tabla_capturas(pdf_plumber, num_pag: int) -> List[RegistroCaptura]:
    """Parsea la tabla de capturas. Puede estar en la misma página que consumos."""
    capturas = []
    
    page = pdf_plumber.pages[num_pag]
    texto = page.extract_text()
    
    # Si dice "No hay registros de capturas" no hay tabla
    if texto and "No hay registros" in texto:
        return []
    
    tables = page.extract_tables()
    
    # La tabla de capturas tiene el mismo formato que consumos (7 cols)
    tablas_consumos = 0
    for tabla in tables:
        if not tabla:
            continue
        header = [str(h).upper() if h else '' for h in tabla[0]]
        header_str = ' '.join(header)
        if "ID" in header_str and "PUNTO CONTROL" in header_str and "TIPO" not in header_str:
            tablas_consumos += 1
            if tablas_consumos == 2:  # La segunda tabla es capturas
                for fila in tabla[1:]:
                    if not fila or sum(1 for c in fila if c is not None) < 3:
                        continue
                    try:
                        captura = RegistroCaptura(
                            id=str(fila[0]).strip() if fila[0] else None,
                            operario=str(fila[1]).strip() if len(fila) > 1 and fila[1] else None,
                            insumo=str(fila[2]).strip() if len(fila) > 2 and fila[2] else None,
                            punto_control=str(fila[3]).strip() if len(fila) > 3 and fila[3] else None,
                            cantidad=int(str(fila[4]).strip()) if len(fila) > 4 and fila[4] and str(fila[4]).strip().isdigit() else None,
                            fecha=str(fila[5]).strip() if len(fila) > 5 and fila[5] else None,
                            comentario=str(fila[6]).strip() if len(fila) > 6 and fila[6] else None,
                        )
                        capturas.append(captura)
                    except (ValueError, IndexError):
                        continue
    
    return capturas


def _parse_relevamiento(pdf_plumber, paginas: list) -> List[PuntoRelevamiento]:
    """
    Parsea las tablas del relevamiento original (punto por punto).
    Las tablas tienen 10 columnas: Subsección, Código, Herramienta, Estado,
    Consumos, Capturas, Repos, Tipo Rep, Operario, Comentario.
    
    IMPORTANTE: pdfplumber genera filas duplicadas con Nones. Las filtramos.
    """
    relevamiento = []
    subseccion_actual = None
    
    for num_pag in paginas:
        if num_pag >= len(pdf_plumber.pages):
            break
        
        page = pdf_plumber.pages[num_pag]
        tables = page.extract_tables()
        
        for tabla in tables:
            if not tabla or len(tabla) < 2:
                continue
            
            # Verificar que es la tabla de relevamiento (10 columnas)
            header = tabla[0]
            if len(header) < 8:
                continue
            
            header_str = ' '.join([str(h).upper() if h else '' for h in header])
            if "ESTADO" not in header_str or "HERRAMIENTA" not in header_str:
                continue
            
            filas_limpias = _limpiar_filas_tabla(tabla[1:])
            
            for fila in filas_limpias:
                if len(fila) < 8:
                    continue
                
                # Actualizar subsección si hay dato
                if fila[0] and str(fila[0]).strip() and str(fila[0]).strip() not in ['-', '']:
                    subseccion_actual = str(fila[0]).strip()
                
                # El código puede estar en col 0 si la subsección no cambió, o col 1
                codigo = None
                herramienta = None
                estado = None
                consumos = 0
                capturas = 0
                repos = 0
                tipo_rep = None
                operario = None
                comentario = None
                
                # Detectar layout de la fila según la tabla
                if len(header) == 10:
                    # [Subsección, Código, Herramienta, Estado, Consumos, Capturas, Repos, TipoRep, Operario, Comentario]
                    codigo = str(fila[1]).strip() if fila[1] else None
                    herramienta = str(fila[2]).strip() if len(fila) > 2 and fila[2] else None
                    estado = str(fila[3]).strip() if len(fila) > 3 and fila[3] else None
                    
                    
                    try:
                        consumos = _parse_float(fila[4]) or 0
                        capturas = int(str(fila[5]).strip()) if len(fila) > 5 and fila[5] and str(fila[5]).strip().isdigit() else 0
                        repos = int(str(fila[6]).strip()) if len(fila) > 6 and fila[6] and str(fila[6]).strip().isdigit() else 0
                    except ValueError:
                        pass
                    
                    tipo_rep = str(fila[7]).strip() if len(fila) > 7 and fila[7] and fila[7] != '-' else None
                    operario = str(fila[8]).strip() if len(fila) > 8 and fila[8] else None
                    comentario = str(fila[9]).strip() if len(fila) > 9 and fila[9] and fila[9] != '-' else None
                else:
                    # Layout alternativo: primera col puede ser código
                    codigo = str(fila[0]).strip() if fila[0] else None
                    if codigo and not re.match(r'^[Cc][Bb]\s*\.?\d+$', codigo):
                        subseccion_actual = codigo
                        codigo = str(fila[1]).strip() if len(fila) > 1 and fila[1] else None
                
                if not codigo or not re.match(r'^[Cc][Bb]\s*\.?\d+$', str(codigo)):
                    continue
                
                punto = PuntoRelevamiento(
                    subseccion=subseccion_actual,
                    codigo=codigo,
                    herramienta=herramienta,
                    estado=estado,
                    consumos=consumos,
                    capturas=capturas,
                    reposiciones=repos,
                    tipo_reposicion=tipo_rep,
                    operario=operario,
                    comentario=comentario,
                )
                relevamiento.append(punto)
    
    return relevamiento


def parsear_mip(filepath: str) -> ParsedMIP:
    """
    Parsea un PDF MIP de roedores y retorna un objeto ParsedMIP.
    
    Estructura:
    - Pág 1: Dashboard + Productos + Comentarios
    - Pág 2: Tabla Consumos + (posible: Tabla Capturas)  
    - Pág 3: Tabla Reposiciones
    - Págs 4-6: Tabla Relevamiento Original
    - Pág 7: Firma
    """
    mip = ParsedMIP()
    
    # ── Texto plano para metadata ──────────────────────────────────────────────
    doc = fitz.open(filepath)
    texto_pag1 = doc[0].get_text() if len(doc) > 0 else ""
    
    # Encabezado
    cliente_match = re.search(r"Resumen MIP - (.+)", texto_pag1)
    if cliente_match:
        partes = cliente_match.group(1).split(" - ")
        if len(partes) >= 2:
            mip.cliente = partes[0].strip()
            mip.sucursal = partes[1].strip()
        else:
            mip.cliente = cliente_match.group(1).strip()
    
    fecha_match = re.search(r"FECHA:\s*(\d{2}/\d{2}/\d{4})", texto_pag1)
    if fecha_match:
        mip.fecha = fecha_match.group(1)
    
    trabajo_match = re.search(r"TRABAJO ID:\s*#?(\d+)", texto_pag1)
    if trabajo_match:
        mip.trabajo_id = trabajo_match.group(1)
    
    # Dashboard
    mip.dashboard = _parse_dashboard(texto_pag1)
    
    # Productos
    mip.productos = _parse_productos(texto_pag1)
    
    # Comentarios
    comentarios_match = re.search(r"Comentarios\s*\n(.+?)(?:\n\n|\Z)", texto_pag1, re.DOTALL)
    if comentarios_match:
        mip.comentarios = comentarios_match.group(1).strip()
    
    doc.close()
    
    # ── Tablas con pdfplumber ──────────────────────────────────────────────────
    with pdfplumber.open(filepath) as pdf:
        num_paginas = len(pdf.pages)
        
        # Pág 2 (índice 1): Consumos y posibles Capturas
        if num_paginas >= 2:
            mip.consumos = _parse_tabla_consumos(pdf, 1)
            mip.capturas = _parse_tabla_capturas(pdf, 1)
        
        # Pág 3 (índice 2): Reposiciones
        if num_paginas >= 3:
            mip.reposiciones = _parse_tabla_reposiciones(pdf, 2)
        
        # Págs 4-6 (índices 3-5): Relevamiento Original
        paginas_relevamiento = list(range(3, min(7, num_paginas - 1)))  # excluye última (firma)
        if paginas_relevamiento:
            mip.relevamiento = _parse_relevamiento(pdf, paginas_relevamiento)
    
    return mip


def es_mip(filepath: str) -> bool:
    """Detecta si un PDF es de tipo MIP (vs Conforme)."""
    try:
        doc = fitz.open(filepath)
        texto = doc[0].get_text() if len(doc) > 0 else ""
        doc.close()
        return "Resumen MIP" in texto or "Dashboard de Actividad MIP" in texto
    except Exception:
        return False
