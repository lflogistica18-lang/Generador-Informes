"""
report_generator_pdf.py — Generación de Informe MIP Mensual en formato PDF

Usa Jinja2 para el renderizado HTML y WeasyPrint para la conversión a PDF.
Incluye generación de gráficos con Matplotlib.
"""
import os
import io
import base64
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('Agg')
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import InformeData
import config

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

def _get_chart_base64():
    """Convierte el gráfico actual de pyplot a base64."""
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _generate_consumos_chart(consumos_data: dict):
    """Genera gráfico de barras de consumos por sector."""
    if not consumos_data:
        return None
    
    sectores = list(consumos_data.keys())
    gramos = list(consumos_data.values())
    
    # Ordenar por consumo descendente
    sorted_pairs = sorted(zip(gramos, sectores), reverse=True)
    
    # Lógica de "Otros Sectores": Mantener el top 8, agrupar el resto
    limite_sectores = 8
    if len(sorted_pairs) > limite_sectores:
        top_sectores = sorted_pairs[:limite_sectores]
        otros_suma = sum(p[0] for p in sorted_pairs[limite_sectores:])
        if otros_suma > 0:
            top_sectores.append((otros_suma, "Otros Sectores"))
        sorted_pairs = top_sectores

    gramos, sectores = zip(*sorted_pairs) if sorted_pairs else ([], [])
    
    plt.figure(figsize=(9, 5))
    color_principal = '#893101' # Burnt Orange
    bars = plt.bar(sectores, gramos, color=color_principal, alpha=0.8)
    
    plt.title('Consumo de Cebos por Sector (gr)', color='#333333', pad=20, fontsize=14, fontweight='bold')
    plt.ylabel('Gramos (gr)', fontsize=11)
    
    # Ajustar etiquetas si hay muchas
    rotation = 20 if len(sectores) < 6 else 45
    plt.xticks(rotation=rotation, ha='right', fontsize=9)
    plt.yticks(fontsize=10)
    
    # Rejilla sutil
    plt.gca().yaxis.grid(True, linestyle='--', alpha=0.3)
    plt.gca().set_axisbelow(True)
    
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.gca().spines['bottom'].set_visible(True)

    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:g}", 
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color=color_principal)
        
    plt.tight_layout()
    return _get_chart_base64()

def _generate_voladores_chart(capturas_uv: list, especies: list):
    """
    Genera gráfico de barras agrupadas para capturas por trampa UV.
    Eje X: Trampas (TUV01, TUV02...).
    Eje Y: Cantidad de capturas.
    Barras agrupadas por especie/plaga.
    """
    if not capturas_uv or not especies:
        return None
    
    n_trampas = len(capturas_uv)
    nombres_trampas = [c.trampa for c in capturas_uv]
    
    # Construir matriz: trampas × especies
    data = np.zeros((n_trampas, len(especies)))
    for i, c in enumerate(capturas_uv):
        for j, esp in enumerate(especies):
            data[i, j] = c.capturas.get(esp, 0)
    
    # Filtrar solo especies con al menos una captura
    totales_esp = np.sum(data, axis=0)
    idx_activos = [i for i, t in enumerate(totales_esp) if t > 0]
    
    if not idx_activos:
        return None
    
    especies_activas = [especies[i] for i in idx_activos]
    data_activa = data[:, idx_activos]
    n_especies = len(especies_activas)
    
    # Configuración del gráfico (ancho dinámico según cantidad de trampas)
    fig, ax = plt.subplots(figsize=(max(9, n_trampas * 0.8), 5))
    
    x = np.arange(n_trampas)
    bar_width = 0.6
    
    # Paleta de colores premium y contrastada
    palette = [
        '#003f5c', # Azul oscuro (Moscas)
        '#444e86', # Azul-Violeta (Mosquitosizado)
        '#955196', # Púrpura (Polillas)
        '#dd5182', # Rosa/Rojo (Lepidópteros)
        '#ff6e54', # Naranja vibrante
        '#ffa600', # Amarillo oro
        '#2a9d8f', # Teal/Verde
        '#e76f51'  # Terracota
    ]
    
    bottoms = np.zeros(n_trampas)
    
    for j, esp in enumerate(especies_activas):
        values = data_activa[:, j]
        bars = ax.bar(x, values, width=bar_width,
                      bottom=bottoms,
                      label=esp,
                      color=palette[j % len(palette)],
                      edgecolor='white', linewidth=0.5,
                      alpha=0.9)
        
        # Opcional: etiquetas de valores dentro o sobre las barras si el valor es significativo
        for i, bar in enumerate(bars):
            h = bar.get_height()
            if h > 5: # Solo mostrar si hay suficiente espacio
                ax.text(bar.get_x() + bar.get_width() / 2, bottoms[i] + h/2,
                        f'{int(h)}', ha='center', va='center', 
                        fontsize=8, color='white', fontweight='bold' if h > 10 else 'normal')
        
        bottoms += values
    
    # Etiquetas de totales arriba de cada barra apilada
    for i, total in enumerate(bottoms):
        if total > 0:
            ax.text(i, total + 0.5, f'{int(total)}', ha='center', va='bottom', 
                    fontsize=9, fontweight='bold', color='#333333')
    
    ax.set_xticks(x)
    ax.set_xticklabels(nombres_trampas, rotation=45 if n_trampas > 10 else 0, ha='center', fontsize=9)
    ax.set_ylabel('Total Capturas (Individuos)', fontsize=10)
    ax.set_title('Presión de Voladores por Trampa UV (Capturas Apiladas)', 
                 color='#333333', pad=20, fontsize=14, fontweight='bold')
    
    # Leyenda mejor posicionada
    ax.legend(title='Especie / Plaga', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False, fontsize=9)
    
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.spines['bottom'].set_visible(True)
    
    plt.tight_layout()
    return _get_chart_base64()

def generate_pdf_report(data: InformeData) -> str:
    """
    Renderiza el informe a PDF y lo guarda en la carpeta outputs.
    Retorna la ruta completa al archivo generado.
    """
    # 1. Preparar datos para el template
    context = data.model_dump()
    
    # 2. Generar imágenes de gráficos
    context['chart_consumos'] = _generate_consumos_chart(data.consumos_por_sector)
    context['chart_voladores'] = _generate_voladores_chart(data.capturas_trampas_uv, data.especies_voladores)
    
    # 3. Renderizar HTML con Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("report.html")
    html_content = template.render(context)
    
    # 4. Generar nombre de archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Informe_MIP_{data.cliente_nombre}_{data.mes}_{data.anio}_{timestamp}.pdf".replace(" ", "_")
    output_path = os.path.join(config.OUTPUTS_DIR, filename)
    
    # 5. Convertir a PDF con WeasyPrint
    try:
        HTML(string=html_content).write_pdf(output_path)
    except Exception as e:
        print(f"ERROR CRÍTICO en WeasyPrint: {str(e)}")
        # Diagnóstico de librerías en caso de fallo
        try:
            import pango
            print(f"Pango disponible")
        except:
            print("Pango NO encontrado o error al cargar")
        
        try:
            import cairo
            print(f"Cairo disponible")
        except:
            print("Cairo NO encontrado o error al cargar")
            
        raise Exception(f"Fallo en la generación de PDF: {str(e)}")
    
    return output_path
