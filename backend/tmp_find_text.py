
import fitz

f = "uploads/42edefdc_MIP_CALSA_-_Planta_4_2026-01-27.pdf"
doc = fitz.open(f)
for i, page in enumerate(doc):
    text = page.get_text()
    if "Externo" in text or "Externo" in text:
        print(f"Pág {i+1} tiene 'Externo'")
    if "EXTERIORES" in text:
        print(f"Pág {i+1} tiene 'EXTERIORES'")
