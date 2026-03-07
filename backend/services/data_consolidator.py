"""
data_consolidator.py — Consolida datos de múltiples visitas del mes

Recibe listas de ParsedConforme y ParsedMIP y genera el InformeData consolidado.
Aplica las reglas de negocio descritas en las instrucciones.
"""
from typing import List, Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import (
    ParsedConforme, ParsedMIP, InformeData,
    DesvioFotografico
)
import re

def clean_text(text: str) -> str:
    """Aplica correcciones ortográficas y de formato básicas a un texto."""
    if not text:
        return ""
    # Quitar múltiples espacios
    text = re.sub(r'\s+', ' ', text)
    # Espacios antes de signos de puntuación
    text = re.sub(r'\s+([,.:;?!])', r'\1', text)
    # Quitar comas repetidas
    text = re.sub(r',+', ',', text)
    # Mayúscula después de punto (simple)
    text = re.sub(r'(\.\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
    return text.strip()

def format_list_es(items: List[str]) -> str:
    """Formatea una lista separada por comas y termina con ' y '."""
    if not items:
        return ""
    # Remover vacíos y duplicados preservando orden
    seen = set()
    unique = []
    for x in items:
        if x and str(x).strip() and x not in seen:
            unique.append(str(x).strip())
            seen.add(x)
            
    if len(unique) == 1:
        return unique[0]
    return ", ".join(unique[:-1]) + " y " + unique[-1]


def _generar_borrador_resumen_roedores(
    observaciones: List[dict],
    capturas: List[dict],
    consumos_sector: dict,
    productos: List[str],
) -> str:
    """Genera un borrador automático del resumen de tratamiento de roedores."""
    partes = []
    
    n_visitas = len(observaciones)
    if n_visitas == 1:
        partes.append("Se realizó 1 monitoreo de los puntos de control instalados (tanto perimetrales como internos).")
    elif n_visitas > 1:
        partes.append(f"Durante el mes se llevaron a cabo {n_visitas} monitoreos de las estaciones de control perimetrales e internas.")
        
    partes.append("En estas visitas se efectuó el acondicionamiento, inspección y reposición de cebos y placas adhesivas según correspondió.")
    
    total_consumo = sum(consumos_sector.values())
    if total_consumo > 0:
        sectores_activos = [k for k, v in consumos_sector.items() if v > 0]
        partes.append(
            f"Se constató un consumo acumulado de {total_consumo:g} gr de rodenticida. "
            f"La mayor actividad se registró en: {format_list_es(sectores_activos)}. "
            "Se implementaron medidas correctivas, reforzando la dotación de cebos en las cebaderas involucradas."
        )
    else:
        partes.append("Durante la inspección de los anillos de seguridad no se detectaron consumos de cebos.")
        
    total_capturas = sum(c.get("capturas", 0) for c in capturas)
    if total_capturas > 0:
        partes.append(f"En cuanto a captura mediante placas adhesivas o trampas de captura viva, se contabilizaron un total de {int(total_capturas)} individuo(s).")
    
    if productos:
        partes.append(f"Para mantener el cerco preventivo activo, se aplicaron los insumos: {format_list_es(productos)}.")
    
    partes.append("Continuamos prestando especial atención en prevenir factores ambientales que favorezcan el anidamiento y tránsito de estas plagas.")
    
    return clean_text(" ".join(partes))


def _generar_borrador_resumen_voladores(
    observaciones: List[dict],
    capturas_uv: list,
    especies: List[str],
) -> str:
    """Genera un borrador automático del resumen de voladores."""
    partes = []
    n_visitas = len(observaciones)
    
    if n_visitas == 0 and not capturas_uv:
        return "No se realizaron inspecciones ni mantenimiento de equipos UV, ni se reportaron monitoreos de voladores en el transcurso de este mes."
        
    if n_visitas > 0:
        partes.append(f"Durante la frecuencia establecida se llevaron a cabo inspecciones a los equipos UV instalados ({n_visitas} visitas de control).")
        partes.append("Se verificó la vida útil de los tubos y se efectuaron los recambios de placas adhesivas que ya presentaban saturación o pérdida de adherencia.")
    
    if capturas_uv:
        partes.append("El conteo de capturas evidencia actividad en las zonas monitoreadas, lo cual es normal considerando la dinámica estacional e instalaciones operativas.")
        if especies:
            partes.append(f"Se identificaron principalmente individuos del tipo {format_list_es(especies)}.")
        partes.append("Para mantener la bioseguridad del sector, sugerimos encarecidamente revisar cerramientos, mallas mosquiteras y asegurar el bloqueo de ingresos de luz desde el exterior durante la noche.")
    else:
        partes.append("En revisión de placas no se evidenciaron saturaciones o indicios extraordinarios que requieran acciones más drásticas.")
        
    return clean_text(" ".join(partes))


def _generar_borrador_resumen_rastreros(aplicaciones: List[dict]) -> str:
    """Genera un borrador automático del resumen de rastreros."""
    partes = []
    
    n_apps = len(aplicaciones)
    if n_apps == 0:
        return "Conforme al cronograma, este mes no se requirieron aplicaciones sistemáticas de desinsectación para el control de rastreros, manteniéndose activo el efecto residual previo."
    
    productos_usados = list({a.get("producto", "") for a in aplicaciones if a.get("producto")})
    prod_str = format_list_es(productos_usados) if productos_usados else 'los productos insecticidas indicados'
    
    if n_apps == 1:
        accion = "Se concretó un servicio operativo preventivo/curativo enfocado al control de arrastreros"
    else:
        accion = f"Se desarrollaron {n_apps} maniobras operativas destinadas a fortalecer la barrera química residual"

    sectores = list({a.get("sectores_tratados", "") for a in aplicaciones if a.get("sectores_tratados")})
    
    # Redacción ajustada para evitar inyecciones de texto crudo kilométrico de los técnicos
    partes.append(f"{accion}. Para estos fines, se utilizaron los productos: {prod_str}.")
    partes.append("Las tareas se desarrollaron sobre las zonas críticas y los sectores acordados previamente en el cronograma de servicios.")
        
    partes.append("Los trabajos abordados transcurrieron de forma habitual, sin novedades que impidan el correcto desarrollo de la aplicación. De esta manera brindamos un contundente control para evitar el establecimiento biológico de plagas.")
    
    return clean_text(" ".join(partes))


def _generar_borrador_conclusion(
    mes: str,
    anio: int,
    resumen_roedores: str,
    resumen_voladores: str,
    resumen_rastreros: str,
) -> str:
    """Genera un borrador de la conclusión general."""
    return (
        f"Durante {mes} {anio}, los tratamientos perimetrales, controles de roedores y "
        "monitoreos de insectos voladores se desarrollaron según lo planificado, "
        "manteniendo la cobertura preventiva en todos los sectores.\n\n"
        "Los resultados de los relevamientos mensuales evidencian el correcto funcionamiento "
        "del programa de Manejo Integrado de Plagas (MIP), con acciones preventivas y correctivas "
        "implementadas oportunamente.\n\n"
        "**Recomendaciones de Exclusión e Higiene:**\n"
        "Se recomienda mantener el orden y la limpieza en todos los sectores, evitar la acumulación "
        "de materiales e insumos en exteriores, y revisar periódicamente los accesos a interiores "
        "para prevenir el ingreso de plagas.\n\n"
        "Todas las oportunidades de mejora, relevamientos mediante imágenes, así como las Hojas de "
        "Seguridad (HDS) y Certificados de los productos utilizados, se encuentran disponibles en el portal web."
    )


def consolidar_datos(
    conformes: List[ParsedConforme],
    mips: List[ParsedMIP],
    informe_data: InformeData,
) -> InformeData:
    """
    Consolida los datos de múltiples visitas del mes en el InformeData.
    Aplica todas las reglas de negocio de la sección 5 de las instrucciones.
    
    Args:
        conformes: Lista de conformes parseados (ya ordenados por fecha)
        mips: Lista de MIPs parseados
        informe_data: Objeto InformeData con datos básicos del informe (cliente, mes, etc.)
    
    Returns:
        InformeData completo con datos consolidados y borradores de resúmenes
    """
    
    # ── Consolidar datos de ROEDORES ──────────────────────────────────────────
    observaciones_roedores = []
    desvios_roedores = []
    consumos_por_sector: Dict[str, float] = {}
    ranking_cebaderas: Dict[str, dict] = {} # Dict de dicts para agrupar por código
    capturas_cebaderas: Dict[str, dict] = {}
    reposiciones_por_tipo: Dict[str, int] = {}
    productos_roedores: set = set()
    campos_faltantes = []

    for conforme in conformes:
        r = conforme.roedores
        if not r:
            continue
        
        # Filtrar visitas "No realizado"
        if r.modo and r.modo.lower() == "no realizado":
            continue
        
        # Tabla de desvíos del mes
        tiene_desvio = bool(conforme.desvios)
        obs_text = r.observaciones or ""
        if tiene_desvio:
            # Buscar referencia cruzada
            obs_text = obs_text + " - Referencia" if obs_text else "- Referencia"
        
        observaciones_roedores.append({
            "fecha": conforme.fecha or "Sin fecha",
            "observaciones": obs_text,
            "tiene_desvio": tiene_desvio,
        })

        # IMPROVED LOGIC: Sumar consumos y capturas de visitas intermedias (no MIP)
        # Solo sumamos si NO existe un MIP para esta fecha (para evitar doble conteo)
        fechas_mips = {m.fecha for m in mips if m.fecha}
        
        if r.consumo and r.consumo > 0:
            if conforme.fecha and conforme.fecha in fechas_mips:
                # Ya está cubierto por el MIP
                pass 
            else:
                sector_gen = "Relevamientos Intermedios"
                consumos_por_sector[sector_gen] = consumos_por_sector.get(sector_gen, 0) + r.consumo
        
        if r.capturas and r.capturas > 0:
             # Si no hay detalle de sector, se agrega como genérico
             capturas_cebaderas["Intermedio"] = {
                 "codigo": "S/D",
                 "herramienta": "Trampa",
                 "subseccion": "Visitas Intermedias",
                 "capturas": capturas_cebaderas.get("Intermedio", {}).get("capturas", 0) + r.capturas
             }
        
        # Desvíos fotográficos de roedores
        for d in conforme.desvios:
            if d.tipo_plaga == "roedores":
                desvios_roedores.append(d)

    # Consolidar datos de los MIPs
    for mip in mips:
        # Productos
        productos_roedores.update(mip.productos)
        
        # Consumos por sector (sumar por punto de control del relevamiento)
        suma_relevamiento_mip = 0
        for punto in mip.relevamiento:
            if punto.consumos > 0:
                subsec = punto.subseccion or "Sin sección"
                subsec = subsec.strip()
                consumos_por_sector[subsec] = consumos_por_sector.get(subsec, 0) + punto.consumos
                suma_relevamiento_mip += punto.consumos
                
                # Para el ranking de cebaderas
                cod = punto.codigo
                if cod:
                    if cod not in ranking_cebaderas:
                        ranking_cebaderas[cod] = {
                            "codigo": cod,
                            "herramienta": punto.herramienta,
                            "subseccion": subsec,
                            "consumo": 0,
                        }
                    ranking_cebaderas[cod]["consumo"] += punto.consumos
            
            # Capturas
            if punto.capturas > 0:
                cod = punto.codigo
                if cod:
                    if cod not in capturas_cebaderas:
                        capturas_cebaderas[cod] = {
                            "codigo": cod,
                            "herramienta": punto.herramienta,
                            "subseccion": punto.subseccion or "Sin sección",
                            "capturas": 0,
                        }
                    capturas_cebaderas[cod]["capturas"] += punto.capturas
        
        # VALIDACIÓN: Si el total del dashboard es mayor que la suma detallada del relevamiento,
        # agregamos la diferencia al primer sector registrado en el MIP para no perder gramos
        # y basarnos siempre en los sectores reales (pedido del usuario).
        total_dashboard = (mip.dashboard.gramos_consumos or 0)
        if total_dashboard > (suma_relevamiento_mip + 0.1): # Umbral de 0.1g para evitar ruido por redondeo
            diferencia = round(total_dashboard - suma_relevamiento_mip, 2)
            # Buscar el primer sector listado en el relevamiento de este MIP
            sectores_mip = [p.subseccion for p in mip.relevamiento if p.subseccion]
            if sectores_mip:
                sector_dif = sectores_mip[0].strip()
            else:
                sector_dif = "Sector Principal"
            consumos_por_sector[sector_dif] = round(consumos_por_sector.get(sector_dif, 0) + diferencia, 2)

        # Reposiciones por tipo
        for repos in mip.reposiciones:
            tipo = repos.tipo or "Sin tipo"
            reposiciones_por_tipo[tipo] = reposiciones_por_tipo.get(tipo, 0) + (repos.cantidad or 0)
    
    # Ordenar ranking de cebaderas (Top 10 por consumo)
    ranking_lista = sorted(
        ranking_cebaderas.values(),
        key=lambda x: x["consumo"],
        reverse=True,
    )[:10]
    
    # Enriquecer con número de ranking
    for i, item in enumerate(ranking_lista):
        item["ranking"] = i + 1
    
    informe_data.observaciones_roedores = observaciones_roedores
    informe_data.consumos_por_sector = consumos_por_sector
    informe_data.ranking_cebaderas = ranking_lista
    informe_data.capturas_cebaderas = list(capturas_cebaderas.values())
    informe_data.reposiciones_por_tipo = reposiciones_por_tipo
    informe_data.productos_roedores = list(productos_roedores)
    informe_data.desvios_roedores = desvios_roedores

    # ── Consolidar datos de VOLADORES ─────────────────────────────────────────
    observaciones_voladores = []
    desvios_voladores = []

    for conforme in conformes:
        v = conforme.voladores
        if not v:
            continue
        if v.modo and v.modo.lower() == "no realizado":
            continue
        
        observaciones_voladores.append({
            "fecha": conforme.fecha or "Sin fecha",
            "observaciones": v.comentarios or "",
        })
        
        for d in conforme.desvios:
            if d.tipo_plaga == "voladores":
                desvios_voladores.append(d)

    informe_data.observaciones_voladores = observaciones_voladores
    informe_data.desvios_voladores = desvios_voladores

    # ── Consolidar datos de RASTREROS ─────────────────────────────────────────
    aplicaciones_rastreros = []
    desvios_rastreros = []

    for conforme in conformes:
        r = conforme.rastreros
        if not r:
            continue
        if r.modo and r.modo.lower() == "no realizado":
            continue
        
        # Detectar datos faltantes de rastreros
        faltantes_visita = []
        if not r.producto:
            faltantes_visita.append("Producto")
        
        aplicacion = {
            "fecha": conforme.fecha or "Sin fecha",
            "producto": r.producto,
            "laboratorio": None,       
            "principio_activo": r.principio_activo,  
            "dosis": r.dosis,             # Valor editado en frontend o nulo
            "cantidad_aplicada": r.cantidad, # Valor editado en frontend o nulo
            "sectores_tratados": r.comentarios,
            "faltantes": faltantes_visita,
        }
        
        # Marcar campos faltantes frecuentes
        for campo_f in ["laboratorio", "principio_activo", "dosis", "cantidad_aplicada"]:
            if aplicacion.get(campo_f) is None:
                faltantes_visita.append(campo_f.replace("_", " ").capitalize())
        
        if faltantes_visita:
            campos_faltantes.append({
                "visita": conforme.fecha or "Sin fecha",
                "seccion": "Rastreros",
                "campos": faltantes_visita,
            })
        
        aplicaciones_rastreros.append(aplicacion)
        
        for d in conforme.desvios:
            if d.tipo_plaga == "rastreros":
                desvios_rastreros.append(d)

    informe_data.aplicaciones_rastreros = aplicaciones_rastreros
    informe_data.desvios_rastreros = desvios_rastreros
    informe_data.campos_faltantes = campos_faltantes

    # ── Agregar campos faltantes de conformes ─────────────────────────────────
    for conforme in conformes:
        if conforme.campos_faltantes:
            campos_faltantes.append({
                "visita": conforme.fecha or "Sin fecha",
                "seccion": "General",
                "campos": conforme.campos_faltantes,
            })

    # ── Campos generales faltantes ────────────────────────────────────────────
    if not informe_data.estaciones_perimetro_externo:
        campos_faltantes.append({
            "visita": "General",
            "seccion": "Roedores",
            "campos": ["Cantidad de estaciones Perimetro Externo"],
        })
    if not informe_data.estaciones_perimetro_interno:
        campos_faltantes.append({
            "visita": "General",
            "seccion": "Roedores",
            "campos": ["Cantidad de estaciones Perimetro Interno"],
        })
    if not informe_data.cantidad_trampas_uv:
        campos_faltantes.append({
            "visita": "General",
            "seccion": "Voladores",
            "campos": ["Cantidad de trampas UV"],
        })

    informe_data.campos_faltantes = campos_faltantes

    # ── Generar borradores de resúmenes ───────────────────────────────────────
    informe_data.resumen_roedores = _generar_borrador_resumen_roedores(
        observaciones=observaciones_roedores,
        capturas=informe_data.capturas_cebaderas,
        consumos_sector=consumos_por_sector,
        productos=list(productos_roedores),
    )
    
    informe_data.resumen_voladores = _generar_borrador_resumen_voladores(
        observaciones=observaciones_voladores,
        capturas_uv=informe_data.capturas_trampas_uv,
        especies=informe_data.especies_voladores,
    )
    
    informe_data.resumen_rastreros = _generar_borrador_resumen_rastreros(
        aplicaciones=aplicaciones_rastreros,
    )
    
    informe_data.conclusion_general = _generar_borrador_conclusion(
        mes=informe_data.mes or "el mes",
        anio=informe_data.anio or 2026,
        resumen_roedores=informe_data.resumen_roedores,
        resumen_voladores=informe_data.resumen_voladores,
        resumen_rastreros=informe_data.resumen_rastreros,
    )

    return informe_data
