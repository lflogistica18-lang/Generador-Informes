#!/usr/bin/env python3
"""Script temporal para analizar la estructura de los PDFs de ejemplo."""
import fitz  # PyMuPDF
import pdfplumber
import os

EJEMPLOS = "/home/lucas/Generador-Informes/Ejemplos"

def analyze_conforme(filepath, name):
    print(f"\n{'='*80}")
    print(f"ANALIZANDO CONFORME: {name}")
    print(f"{'='*80}")
    
    # Extraer texto con PyMuPDF
    doc = fitz.open(filepath)
    print(f"Páginas: {len(doc)}")
    
    for i, page in enumerate(doc):
        text = page.get_text()
        print(f"\n--- Página {i+1} ---")
        print(text[:3000] if len(text) > 3000 else text)
        
        # Contar imágenes
        images = page.get_images()
        if images:
            print(f"\n[IMÁGENES en página {i+1}: {len(images)}]")
    
    doc.close()

def analyze_mip(filepath, name):
    print(f"\n{'='*80}")
    print(f"ANALIZANDO MIP: {name}")
    print(f"{'='*80}")
    
    # Extraer texto con PyMuPDF
    doc = fitz.open(filepath)
    print(f"Páginas: {len(doc)}")
    
    for i, page in enumerate(doc):
        text = page.get_text()
        print(f"\n--- Página {i+1} ---")
        print(text[:3000] if len(text) > 3000 else text)
    
    doc.close()
    
    # Extraer tablas con pdfplumber
    print(f"\n--- TABLAS (pdfplumber) ---")
    with pdfplumber.open(filepath) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables:
                print(f"\nPágina {i+1}: {len(tables)} tabla(s)")
                for j, table in enumerate(tables):
                    print(f"  Tabla {j+1}: {len(table)} filas x {len(table[0]) if table else 0} cols")
                    for row in table[:5]:  # primeras 5 filas
                        print(f"    {row}")
                    if len(table) > 5:
                        print(f"    ... ({len(table)-5} filas más)")

def analyze_reference(filepath, name):
    print(f"\n{'='*80}")
    print(f"ANALIZANDO INFORME DE REFERENCIA: {name}")
    print(f"{'='*80}")
    
    doc = fitz.open(filepath)
    print(f"Páginas: {len(doc)}")
    
    for i, page in enumerate(doc):
        text = page.get_text()
        print(f"\n--- Página {i+1} (primeros 2000 chars) ---")
        print(text[:2000] if len(text) > 2000 else text)
        
        images = page.get_images()
        if images:
            print(f"\n[IMÁGENES en página {i+1}: {len(images)}]")
    
    doc.close()

if __name__ == "__main__":
    files = os.listdir(EJEMPLOS)
    
    for f in sorted(files):
        if not f.endswith('.pdf'):
            continue
        filepath = os.path.join(EJEMPLOS, f)
        
        if f.startswith("Conforme"):
            analyze_conforme(filepath, f)
        elif f.startswith("MIP_"):
            analyze_mip(filepath, f)
        elif f.startswith("Informe"):
            analyze_reference(filepath, f)
