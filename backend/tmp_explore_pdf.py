
import sys
import os
import pdfplumber

sys.path.insert(0, os.path.dirname(__file__))

f = "uploads/42edefdc_MIP_CALSA_-_Planta_4_2026-01-27.pdf"
full_path = os.path.join(os.path.dirname(__file__), f)

with pdfplumber.open(full_path) as pdf:
    # Ver tablas de todas las páginas (excepto la 1 que es dashboard)
    for i in range(1, len(pdf.pages)):
        page = pdf.pages[i]
        print(f"\n--- EXPLORANDO PÁGINA {i+1} ---")
        tables = page.extract_tables()
        for t_idx, t in enumerate(tables):
            if not t or not t[0]: continue
            header = [str(h).upper() for h in t[0] if h]
            header_str = " ".join(header)
            print(f"  Tabla {t_idx} Header: {header_str[:100]}...")
            
            # Ver si es la de relevamiento
            if "ESTADO" in header_str and "CONSUMOS" in header_str:
                print(f"    ¡ES RELEVAMIENTO!")
                # Ver si está CB004 en esta tabla
                for row in t:
                    if row and "CB004" in str(row):
                         print(f"    Fila CB004: {row}")
