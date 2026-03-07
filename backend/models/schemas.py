"""
schemas.py — Modelos Pydantic para el Generador de Informes MIP
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


# ─── Estructuras de datos extraídos de PDFs ───────────────────────────────────

class ServicioRastreros(BaseModel):
    tipo: str = "Desinsectación de Rastreros"
    modo: Optional[str] = None          # Preventiva / Correctiva / No realizado
    maquinarias: Optional[str] = None
    producto: Optional[str] = None
    principio_activo: Optional[str] = None  # Agregado para edición manual
    dosis: Optional[str] = None         # Agregado para edición manual
    cantidad: Optional[str] = None      # Agregado para edición manual
    avistamiento: Optional[str] = None  # Si / No
    comentarios: Optional[str] = None


class ServicioVoladores(BaseModel):
    tipo: str = "Desinsectación de Mosquitos"
    modo: Optional[str] = None
    producto: Optional[str] = None
    avistamiento: Optional[str] = None
    comentarios: Optional[str] = None


class ServicioRoedores(BaseModel):
    tipo: str = "Desratización"
    modo: Optional[str] = None          # Mip / Preventiva / Correctiva
    consumo: Optional[float] = None
    avistamiento: Optional[int] = None
    reposicion: Optional[int] = None
    capturas: Optional[int] = None
    observaciones: Optional[str] = None


class ReceptorServicio(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    dni: Optional[str] = None
    puesto: Optional[str] = None


class DesvioFotografico(BaseModel):
    sector: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_plaga: Optional[str] = None    # roedores / voladores / rastreros
    imagen_base64: Optional[str] = None
    imagen_path: Optional[str] = None


class ParsedConforme(BaseModel):
    """Datos extraídos de un PDF Conforme (Informe de Visita)."""
    # Encabezado
    track_id: Optional[str] = None
    cliente: Optional[str] = None
    direccion: Optional[str] = None
    fecha: Optional[str] = None
    operario: Optional[str] = None
    ingreso: Optional[str] = None
    egreso: Optional[str] = None
    # Servicios
    rastreros: Optional[ServicioRastreros] = None
    voladores: Optional[ServicioVoladores] = None
    roedores: Optional[ServicioRoedores] = None
    # Receptor
    receptor: Optional[ReceptorServicio] = None
    # Desvíos
    desvios: List[DesvioFotografico] = []
    # Campos faltantes detectados
    campos_faltantes: List[str] = []


class RegistroConsumo(BaseModel):
    id: Optional[str] = None
    operario: Optional[str] = None
    insumo: Optional[str] = None
    punto_control: Optional[str] = None
    cantidad: Optional[float] = None
    fecha: Optional[str] = None
    comentario: Optional[str] = None


class RegistroReposicion(BaseModel):
    id: Optional[str] = None
    operario: Optional[str] = None
    insumo: Optional[str] = None
    tipo: Optional[str] = None          # Consumo / Degradado / Mantenimiento / Faltante
    punto_control: Optional[str] = None
    cantidad: Optional[int] = None
    fecha: Optional[str] = None
    comentario: Optional[str] = None


class RegistroCaptura(BaseModel):
    id: Optional[str] = None
    operario: Optional[str] = None
    insumo: Optional[str] = None
    punto_control: Optional[str] = None
    cantidad: Optional[int] = None
    fecha: Optional[str] = None
    comentario: Optional[str] = None


class PuntoRelevamiento(BaseModel):
    subseccion: Optional[str] = None
    codigo: Optional[str] = None
    herramienta: Optional[str] = None
    estado: Optional[str] = None       # Sin Novedad / Activa / Bloqueada / No Relevado
    consumos: float = 0
    capturas: float = 0
    reposiciones: float = 0
    tipo_reposicion: Optional[str] = None
    operario: Optional[str] = None
    comentario: Optional[str] = None


class DashboardMIP(BaseModel):
    total_consumos: int = 0
    gramos_consumos: float = 0
    total_capturas: float = 0
    total_reposiciones: float = 0
    gramos_reposiciones: float = 0
    placas_reposicion: float = 0
    total_operarios: int = 0


class ParsedMIP(BaseModel):
    """Datos extraídos de un PDF MIP (Registro de Roedores)."""
    cliente: Optional[str] = None
    sucursal: Optional[str] = None
    fecha: Optional[str] = None
    trabajo_id: Optional[str] = None
    dashboard: Optional[DashboardMIP] = None
    productos: List[str] = []
    comentarios: Optional[str] = None
    consumos: List[RegistroConsumo] = []
    capturas: List[RegistroCaptura] = []
    reposiciones: List[RegistroReposicion] = []
    relevamiento: List[PuntoRelevamiento] = []


# ─── Estructuras de Clientes ──────────────────────────────────────────────────

class Sucursal(BaseModel):
    id: Optional[str] = None
    nombre: str
    direccion: Optional[str] = None


class Cliente(BaseModel):
    id: Optional[str] = None
    nombre: str
    sucursales: List[Sucursal] = []


# ─── Estructuras del Informe ──────────────────────────────────────────────────

class CapturaTrampaUV(BaseModel):
    """Datos de captura manual por trampa UV."""
    trampa: str              # TUV01, TUV02...
    capturas: dict           # {"Moscas": 8, "Mosca de la Fruta": 0, ...}


class InformeData(BaseModel):
    """Datos consolidados para generar el Informe MIP Mensual."""
    cliente_id: Optional[str] = None
    cliente_nombre: Optional[str] = None
    sucursal_nombre: Optional[str] = None
    sucursal_direccion: Optional[str] = None
    mes: Optional[str] = None
    anio: Optional[int] = None

    # Generalidades
    estaciones_perimetro_externo: Optional[int] = None
    estaciones_perimetro_interno: Optional[int] = None
    cantidad_trampas_uv: Optional[int] = None
    codigos_trampas_uv: List[str] = []
    especies_voladores: List[str] = []
    configuracion_roedores: Optional[dict] = None

    # Datos consolidados de roedores
    observaciones_roedores: List[dict] = []  # [{fecha, observaciones, tiene_desvio}]
    consumos_por_sector: dict = {}
    ranking_cebaderas: List[dict] = []
    capturas_cebaderas: List[dict] = []
    reposiciones_por_tipo: dict = {}
    productos_roedores: List[str] = []
    desvios_roedores: List[DesvioFotografico] = []

    # Datos de voladores
    observaciones_voladores: List[dict] = []  # [{fecha, observaciones}]
    capturas_trampas_uv: List[CapturaTrampaUV] = []
    desvios_voladores: List[DesvioFotografico] = []

    # Datos de rastreros
    aplicaciones_rastreros: List[dict] = []
    desvios_rastreros: List[DesvioFotografico] = []

    # Otras plagas / Incidencias generales
    desvios_otros: List[DesvioFotografico] = []

    # Resúmenes (editables por el usuario)
    resumen_roedores: Optional[str] = None
    resumen_voladores: Optional[str] = None
    resumen_rastreros: Optional[str] = None
    conclusion_general: Optional[str] = None

    # Gráficos generados (base64)
    chart_consumos: Optional[str] = None
    chart_voladores: Optional[str] = None

    # Datos faltantes detectados
    campos_faltantes: List[dict] = []


class UploadResponse(BaseModel):
    """Respuesta al subir y parsear PDFs."""
    archivos_procesados: int
    conformes: List[ParsedConforme] = []
    mips: List[ParsedMIP] = []
    errores: List[str] = []
    campos_faltantes: List[dict] = []
