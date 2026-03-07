"""
reports.py — Router de FastAPI para consolidación y generación de informes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os

from models.schemas import InformeData
from services.data_consolidator import consolidar_datos
from services.report_generator_pdf import generate_pdf_report
from services.report_generator_pdf import generate_pdf_report
import config

router = APIRouter()

@router.post("/consolidate")
async def consolidate_report(data: dict):
    """
    Consolida los datos de múltiples visitas en un InformeData listo para generación.
    Recibe: {conformes: [...], mips: [...], informe_base: {...}}
    """
    try:
        from models.schemas import ParsedConforme, ParsedMIP
        
        from services.report_generator_pdf import _generate_consumos_chart, _generate_voladores_chart
        
        conformes = [ParsedConforme(**c) for c in data.get("conformes", [])]
        mips = [ParsedMIP(**m) for m in data.get("mips", [])]
        informe_base = InformeData(**data.get("informe_base", {}))
        
        informe = consolidar_datos(conformes, mips, informe_base)
        
        # Calcular estaciones dinámicamente según configuración para el cuadro superior
        if informe.configuracion_roedores and informe.configuracion_roedores.get("sectores"):
            tot_cb = 0
            tot_pg = 0
            for sec in informe.configuracion_roedores["sectores"]:
                tot_cb += int(sec.get("cantidad_cb") or 0)
                tot_pg += int(sec.get("cantidad_pg") or 0)
            
            informe.estaciones_perimetro_externo = tot_cb
            informe.estaciones_perimetro_interno = tot_pg
        
        # Generar gráficos base64 iniciales
        informe.chart_consumos = _generate_consumos_chart(informe.consumos_por_sector)
        informe.chart_voladores = _generate_voladores_chart(informe.capturas_trampas_uv, informe.especies_voladores)
        
        return informe.model_dump()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pdf")
async def generate_pdf(informe_data: dict):
    """Genera el Informe MIP Mensual en formato PDF."""
    try:
        informe = InformeData(**informe_data)
        filepath = generate_pdf_report(informe)
        
        if os.path.exists(filepath):
            return FileResponse(
                path=filepath, 
                filename=os.path.basename(filepath),
                media_type='application/pdf'
            )
        raise HTTPException(status_code=500, detail="Error al generar el archivo PDF")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-charts")
async def update_charts(informe_data: dict):
    """Actualiza los gráficos base64 basados en los datos actuales."""
    try:
        from services.report_generator_pdf import _generate_consumos_chart, _generate_voladores_chart
        informe = InformeData(**informe_data)
        
        informe.chart_consumos = _generate_consumos_chart(informe.consumos_por_sector)
        informe.chart_voladores = _generate_voladores_chart(informe.capturas_trampas_uv, informe.especies_voladores)
        
        return informe.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
