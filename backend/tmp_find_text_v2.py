
import fitz
import os

base_path = os.path.dirname(__file__)
f = os.path.join(base_path, "uploads/42edefdc_MIP_CALSA_-_Planta_4_2026-01-27.pdf")

doc = fitz.open(f)
for i, page in enumerate(doc):
    text = page.get_text()
    if "Externo" in text:
        print(f"Pág {i+1} tiene 'Externo'")
    if "EXTERIORES" in text:
        print(f"Pág {i+1} tiene 'EXTERIORES'")
    if i >= 3: # Páginas de relevamiento
        # Buscar la línea que tenga CB004 y un 4
        lines = text.split('\n')
        for line in lines:
            if "CB004" in line:
                print(f"Pág {i+1} - Línea CB004: {line.strip()}")
