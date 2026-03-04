
import os
import sys
import glob

# Add backend directory to sys.path
sys.path.append(os.getcwd())

from services.pdf_parser_mip import parsear_mip
from services.pdf_parser_conforme import parsear_conforme
from services.data_consolidator import consolidar_datos
from services.report_generator_pdf import generate_pdf_report
from models.schemas import InformeData


def reproduce_issue():
    print("Iniciando reproducción del error...")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    uploads_dir = os.path.join(project_root, "Planta 4 Enero")
    
    # Selecting files based on user hint "Planta 4 Enero"
    # Looking for MIPs
    mip_files = glob.glob(os.path.join(uploads_dir, "*mip_calsa_-_planta_4_2026-01*.pdf"))
    
    # Looking for Conformes (excluding MIPs)
    all_pdfs = glob.glob(os.path.join(uploads_dir, "*.pdf"))
    conforme_files = [f for f in all_pdfs if "mip_calsa" not in f and not f.endswith("Zone.Identifier")]
    
    print(f"MIPs encontrados: {len(mip_files)}")
    print(f"Conformes seleccionados: {len(conforme_files)}")
    
    mips = []
    conformes = []
    
    try:
        # 1. Parse MIPs
        for f in mip_files:
            print(f"Parseando MIP: {os.path.basename(f)}")
            mip = parsear_mip(f)
            print(f"  -> Total Consumos: {mip.dashboard.total_consumos}")
            print(f"  -> Gramos Consumos: {mip.dashboard.gramos_consumos}")
            mips.append(mip)
            
        # 2. Parse Conformes
        for f in conforme_files:
            # parsear_conforme takes only filepath
            conf = parsear_conforme(f)
            if conf.roedores:
                 print(f"  -> Conforme {os.path.basename(f)} Roedores Consumo: {conf.roedores.consumo}")
            conformes.append(conf)
            
        print("Preparando InformeData...")
        # 3. Create initial InformeData
        informe_data = InformeData(
            cliente_nombre="Calsa Planta 4",
            sucursal_nombre="Planta 4",
            mes="Enero",
            anio=2026
        )
        
        print("Consolidando datos...")
        # 4. Consolidate Data
        informe_consolidado = consolidar_datos(conformes, mips, informe_data)
        
        print("Generando PDF...")
        # 5. Generate PDF
        pdf_path = generate_pdf_report(informe_consolidado)
        print(f"PDF generado exitosamente en: {pdf_path}")
        
    except Exception as e:
        print("\n!!! ERROR DETECTADO !!!")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce_issue()
