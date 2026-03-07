
import sys
import os
import pdfplumber

sys.path.insert(0, os.path.dirname(__file__))

f = "uploads/42edefdc_MIP_CALSA_-_Planta_4_2026-01-27.pdf"
full_path = os.path.join(os.path.dirname(__file__), f)

with pdfplumber.open(full_path) as pdf:
    # Mirar todas las páginas del relevamiento
    for i in range(3, len(pdf.pages)):
        page = pdf.pages[i]
        print(f"\n--- PÁGINA {i+1} ---")
        tables = page.extract_tables()
        for t in tables:
            for row in t:
                # Filtrar filas vacías
                if any(row):
                    print(row)
