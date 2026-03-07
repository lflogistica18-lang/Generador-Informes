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


def _expandir_aplicacion_rastreros(aplicacion: dict) -> List[dict]:
    """
    Si el campo 'producto' contiene múltiples productos (separados por +, /, o ,),
    intenta expandir la aplicación en múltiples entradas para un desglose visual claro.
    """
    def split_clean(txt, seps):
        if not txt: return []
        # Escaparlos para regex
        patron = "|".join([re.escape(s) for s in seps])
        return [p.strip() for p in re.split(patron, txt) if p.strip()]

    separadores = ["+", " / ", " - ", " y "]
    
    prod_orig = aplicacion.get("producto") or ""
    # Si contiene el separador, procedemos
    if not any(s in prod_orig for s in separadores):
        return [aplicacion]

    prods = split_clean(prod_orig, separadores)
    if len(prods) <= 1:
        return [aplicacion]

    pa_orig = aplicacion.get("principio_activo") or ""
    dosis_orig = aplicacion.get("dosis") or ""
    cant_orig = aplicacion.get("cantidad_aplicada") or ""

    pas = split_clean(pa_orig, separadores)
    dosis_list = split_clean(dosis_orig, separadores)
    cants_list = split_clean(cant_orig, separadores)

    expandidas = []
    for i, p in enumerate(prods):
        new_app = aplicacion.copy()
        new_app["producto"] = p
        
        # Mapear PA, Dosis y Cant si tienen datos correspondientes
        if len(pas) == len(prods):
            new_app["principio_activo"] = pas[i]
        elif len(pas) > i:
             new_app["principio_activo"] = pas[i]
        
        if len(dosis_list) == len(prods):
            new_app["dosis"] = dosis_list[i]
        elif len(dosis_list) > i:
            new_app["dosis"] = dosis_list[i]
            
        if len(cants_list) == len(prods):
            new_app["cantidad_aplicada"] = cants_list[i]
        elif len(cants_list) > i:
             new_app["cantidad_aplicada"] = cants_list[i]
             
        expandidas.append(new_app)
    
    return expandidas


def _generar_borrador_resumen_roedores(
    observaciones: List[dict],
    capturas: List[dict],
    consumos_sector: dict,
    productos: List[str],
) -> str:
    """Genera un borrador estructurado del resumen de tratamiento de roedores."""
    n_visitas = len(observaciones)
    
    # Encabezado
    encabezado = "Se realizaron las tareas de control y mantenimiento del cerco sanitario contra roedores, cubriendo tanto los perímetros externos como los sectores internos."
    
    # Cuerpo (Desglose informativo)
    cuerpo_partes = []
    if n_visitas > 0:
        cuerpo_partes.append(f"Durante este mes se concretaron {n_visitas} monitoreos sistemáticos.")
    
    total_consumo = sum(consumos_sector.values())
    if total_consumo > 0:
        sectores_activos = [k for k, v in consumos_sector.items() if v > 0]
        cuerpo_partes.append(f"Se registró un consumo acumulado de {total_consumo:g}g de rodenticida, con mayor incidencia en {format_list_es(sectores_activos)}.")
        cuerpo_partes.append("Se procedió al refuerzo preventivo en los puntos con mayor actividad para asegurar el control de las colonias.")
    else:
        cuerpo_partes.append("El monitoreo de las estaciones no evidenció consumo de cebos, indicando que las barreras preventivas se encuentran operativas y sin presión de plaga.")

    total_capturas = sum(c.get("capturas", 0) for c in capturas)
    if total_capturas > 0:
        cuerpo_partes.append(f"Se registraron {int(total_capturas)} capturas en dispositivos mecánicos/adhesivos, las cuales fueron debidamente retiradas y los equipos reacondicionados.")

    if productos:
        cuerpo_partes.append(f"Insumos aplicados: {format_list_es(productos)}.")
    
    # Cierre
    cierre = "Mantendremos el seguimiento exhaustivo de todos los anillos de seguridad para prevenir incursiones externas y garantizar la inocuidad de las instalaciones."
    
    full_text = f"{encabezado}\n\n{' '.join(cuerpo_partes)}\n\n{cierre}"
    return clean_text(full_text)


def _generar_borrador_resumen_voladores(
    observaciones: List[dict],
    capturas_uv: list,
    especies: List[str],
) -> str:
    """Genera un borrador estructurado del resumen de voladores."""
    n_visitas = len(observaciones)
    
    # Encabezado
    encabezado = "Se ejecutó el plan de monitoreo y control de insectos voladores mediante la revisión y mantenimiento de las trampas de luz UV instaladas en sectores estratégicos."
    
    # Cuerpo
    cuerpo_partes = []
    if n_visitas > 0:
        cuerpo_partes.append(f"Se realizaron {n_visitas} inspecciones técnicas durante el mes.")
    
    if capturas_uv:
        cuerpo_partes.append("El conteo de capturas muestra actividad insectil dentro de los parámetros esperables para la época y el rubro.")
        if especies:
            cuerpo_partes.append(f"Se identificó presencia de {format_list_es(especies)}.")
        cuerpo_partes.append("Se procedió al recambio de láminas adhesivas saturadas y a la limpieza de las unidades para garantizar la máxima capacidad de atracción.")
    else:
        cuerpo_partes.append("No se registraron niveles críticos de capturas en los equipos, confirmando la efectividad de las medidas de exclusión actuales.")

    # Cierre
    cierre = "Se recomienda mantener el cierre de puertas y asegurar la hermeticidad de las mallas mosquiteras para minimizar el ingreso de individuos desde el exterior."
    
    full_text = f"{encabezado}\n\n{' '.join(cuerpo_partes)}\n\n{cierre}"
    return clean_text(full_text)


def _generar_borrador_resumen_rastreros(aplicaciones: List[dict]) -> str:
    """Genera un borrador estructurado del resumen de rastreros."""
    n_apps = len(aplicaciones)
    
    # Encabezado
    encabezado = "Se llevaron a cabo aplicaciones de desinsectación orientadas a mantener el control sobre insectos rastreros y arácnidos en áreas críticas y comunes."
    
    # Cuerpo
    cuerpo_partes = []
    if n_apps > 0:
        sectores = list({a.get("sectores_tratados", "") for a in aplicaciones if a.get("sectores_tratados")})
        productos = list({a.get("producto", "") for a in aplicaciones if a.get("producto")})
        cuerpo_partes.append(f"Se concretaron {n_apps} aplicaciones químicas en {format_list_es(sectores)}.")
        if productos:
            cuerpo_partes.append(f"Se utilizaron productos de amplio espectro residual: {format_list_es(productos)}.")
        cuerpo_partes.append("Las tareas se enfocaron en puntos de anidamiento y vías de tránsito identificadas durante las inspecciones previas.")
    else:
        cuerpo_partes.append("No fue necesaria la aplicación de refuerzos químicos extraordinarios durante este periodo, manteniéndose el control preventivo mediante las barreras residuales existentes.")

    # Cierre
    cierre = "Estas acciones reafirman el compromiso con la higiene ambiental, evitando la proliferación de plagas que pudieran comprometer la operatividad."
    
    full_text = f"{encabezado}\n\n{' '.join(cuerpo_partes)}\n\n{cierre}"
    return clean_text(full_text)


def _generar_borrador_conclusion(
    mes: str,
    anio: int,
    consumo_tot: float,
    n_desvios_roedores: int,
    n_desvios_voladores: int,
    n_desvios_rastreros: int,
    n_desvios_otros: int,
) -> str:
    """Genera un borrador de la conclusión general basada en los datos del mes."""
    encabezado = f"Durante {mes} {anio}, el programa de Manejo Integrado de Plagas (MIP) se desarrolló cumpliendo con las frecuencias y metodologías planificadas."
    
    # Roedores
    if consumo_tot > 0:
        txt_roedores = f"En el control de roedores, se registró actividad con un consumo acumulado de {consumo_tot:g}g, procediendo al refuerzo de los puntos críticos."
    else:
        txt_roedores = "El control de roedores se mantuvo estable sin registros de consumos significativos en los anillos de seguridad."
    
    # Hallazgos / Desvíos
    total_desvios = n_desvios_roedores + n_desvios_voladores + n_desvios_rastreros + n_desvios_otros
    if total_desvios > 0:
        detalles = []
        if n_desvios_roedores > 0: detalles.append(f"{n_desvios_roedores} en roedores")
        if n_desvios_voladores > 0: detalles.append(f"{n_desvios_voladores} en voladores")
        if n_desvios_rastreros > 0: detalles.append(f"{n_desvios_rastreros} en rastreros")
        if n_desvios_otros > 0: detalles.append(f"{n_desvios_otros} estructurales/otros")
        txt_desvios = f"Se detectaron un total de {total_desvios} oportunidades de mejora ({', '.join(detalles)}), las cuales requieren atención para optimizar la hermeticidad y bioseguridad del predio."
    else:
        txt_desvios = "No se detectaron desvíos estructurales graves, recomendando mantener las condiciones actuales de orden y limpieza."

    cierre = (
        "**Recomendaciones de Exclusión e Higiene:**\n"
        "Se recomienda mantener el orden y la limpieza en todos los sectores, evitar la acumulación "
        "de materiales e insumos en exteriores, y revisar periódicamente los accesos a interiores "
        "para prevenir el ingreso de plagas.\n\n"
        "Todas las oportunidades de mejora, relevamientos mediante imágenes, así como las Hojas de "
        "Seguridad (HDS) y Certificados de los productos utilizados, se encuentran disponibles en el portal web."
    )

    cuerpo = f"{encabezado}\n\n{txt_roedores} {txt_desvios}\n\n{cierre}"
    return cuerpo


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
    desvios_roedores = []
    desvios_voladores = []
    desvios_rastreros = []
    desvios_otros = []
    campos_faltantes = []

    for conforme in conformes:
        # 1. Desvíos fotográficos (Siempre procesar por cada visita)
        for d in conforme.desvios:
            tp = (d.tipo_plaga or "").lower()
            if tp == "roedores":
                desvios_roedores.append(d)
            elif tp == "voladores":
                desvios_voladores.append(d)
            elif tp == "rastreros":
                desvios_rastreros.append(d)
            else:
                desvios_otros.append(d)

        # 2. Relevamientos de Roedores
        r = conforme.roedores
        if not r:
            continue
        
        # Filtrar visitas "No realizado"
        if r.modo and r.modo.lower() == "no realizado":
            continue
        
        # Lógica de texto automático si no hay observaciones ni desvíos
        obs_text = r.observaciones or ""
        # Solo verificamos desvios de roedores para este texto
        tiene_desvio_roedores = any(d.tipo_plaga == "roedores" for d in conforme.desvios)
        
        if not obs_text and not tiene_desvio_roedores:
            obs_text = "Monitoreo de estaciones de control: Se monitorearon estaciones de control, no se registraron desvíos."
        elif tiene_desvio_roedores:
            prefix = "Monitoreo de estaciones de control: "
            obs_text = prefix + (obs_text + " - Referencia fotográfica" if obs_text else "Se registraron hallazgos - Ver referencia")
        else:
            obs_text = f"Monitoreo de estaciones de control: {obs_text}"
        
        observaciones_roedores.append({
            "fecha": conforme.fecha or "Sin fecha",
            "observaciones": obs_text,
            "tiene_desvio": tiene_desvio_roedores,
        })

        # Sumar consumos y capturas de visitas intermedias
        fechas_mips = {m.fecha for m in mips if m.fecha}
        
        if r.consumo and r.consumo > 0:
            if not (conforme.fecha and conforme.fecha in fechas_mips):
                sector_gen = "Relevamientos Intermedios"
                consumos_por_sector[sector_gen] = consumos_por_sector.get(sector_gen, 0) + r.consumo
        
        if r.capturas and r.capturas > 0:
             capturas_cebaderas["Intermedio"] = {
                 "codigo": "S/D",
                 "herramienta": "Trampa",
                 "subseccion": "Visitas Intermedias",
                 "capturas": capturas_cebaderas.get("Intermedio", {}).get("capturas", 0) + r.capturas
             }

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
            # Buscar el primer sector que sea "Externo" para volcar la diferencia
            sectores_mip = [p.subseccion for p in mip.relevamiento if p.subseccion]
            sector_dif = "Sector Principal" # Fallback
            
            if sectores_mip:
                # Intentar encontrar uno que diga "extern"
                externo = next((s for s in sectores_mip if "extern" in s.lower()), None)
                if externo:
                    sector_dif = externo.strip()
                else:
                    sector_dif = sectores_mip[0].strip()
            
            consumos_por_sector[sector_dif] = round(consumos_por_sector.get(sector_dif, 0) + diferencia, 2)

        # Reposiciones por tipo
        for repos in mip.reposiciones:
            tipo = repos.tipo or "Sin tipo"
            reposiciones_por_tipo[tipo] = reposiciones_por_tipo.get(tipo, 0) + (repos.cantidad or 0)

        # Agregar comentario del MIP a la tabla de monitoreo
        if mip.comentarios or mip.fecha:
            mip_obs = mip.comentarios or "Sin observaciones registradas en planilla."
            observaciones_roedores.append({
                "fecha": mip.fecha or "Sin fecha",
                "observaciones": f"Monitoreo de estaciones de control: {mip_obs}",
                "tiene_desvio": False, # MIPs usualmente no traen el link a la foto directamente aquí
            })
    
    # Ordenar tabla de monitoreo/observaciones por fecha
    def parse_fecha(f_str):
        try:
            # Formato esperado DD/MM/YYYY
            partes = f_str.split("/")
            if len(partes) == 3:
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
        except:
            pass
        return "0000-00-00"

    observaciones_roedores.sort(key=lambda x: parse_fecha(x["fecha"]))

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
    for conforme in conformes:
        v = conforme.voladores
        if not v or (v.modo and v.modo.lower() == "no realizado"):
            continue
        observaciones_voladores.append({
            "fecha": conforme.fecha or "Sin fecha",
            "observaciones": v.comentarios or "Sin observaciones registradas.",
        })

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
        
        # Expandir si hay múltiples productos
        aplicaciones_expandidas = _expandir_aplicacion_rastreros(aplicacion)
        aplicaciones_rastreros.extend(aplicaciones_expandidas)
        
    informe_data.aplicaciones_rastreros = aplicaciones_rastreros
    informe_data.desvios_rastreros = desvios_rastreros
    # Nuevo campo para desvíos de 'otros' (ej: palomas)
    informe_data.desvios_otros = desvios_otros
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
        consumo_tot=sum(consumos_por_sector.values()),
        n_desvios_roedores=len(desvios_roedores),
        n_desvios_voladores=len(desvios_voladores),
        n_desvios_rastreros=len(desvios_rastreros),
        n_desvios_otros=len(desvios_otros),
    )

    return informe_data
