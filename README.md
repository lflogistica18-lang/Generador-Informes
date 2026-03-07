# Generador de Informes MIP & Visita de Control

Sistema profesional para la consolidación de datos de control de plagas y generación automática de informes en PDF. Diseñado para transformar múltiples reportes operativos en un único documento de alta calidad para el cliente final.

## 🚀 Características Principales

- **Consolidación Inteligente**: Procesa simultáneamente archivos de tipo "MIP" (Registros de Roedores) e "Informes de Visita" (Conforme).
- **Control de Roedores Avanzado**: Configuración dinámica de múltiples sectores (Cebaderas, Perímetro, etc.) con conteo automático de dispositivos (CB y PG).
- **Resúmenes Automáticos**: Generación de textos descriptivos con gramática natural, corrección ortotipográfica y eliminación de redundancias.
- **Evidencia Fotográfica**: Extracción automática de imágenes de desvíos con sus descripciones reales y recomendaciones técnicas.
- **Visualización de Datos**: Gráficos dinámicos de capturas en trampas de luz (UV) por dispositivo.
- **Exportación Profesional**: Generación de PDF optimizado con diseño institucional premium.

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.12 + FastAPI
- **Procesamiento PDF**: PyMuPDF (fitz), pdfplumber
- **Generación PDF**: WeasyPrint + Jinja2 (Templates HTML)
- **Frontend**: React + Vite + Tailwind CSS
- **Gestión de Estado**: Pinia/Zustand pattern

## 📦 Estructura del Proyecto

```text
├── backend/
│   ├── main.py              # Punto de entrada de la API
│   ├── routers/             # Endpoints (Upload, Reports, Clients)
│   ├── services/            # Lógica de negocio (Parsers, Consolidator)
│   ├── models/              # Schemas de Pydantic
│   ├── templates/           # Plantillas HTML para el PDF
│   └── requirements.txt     # Dependencias de Python
├── frontend/
│   ├── src/                 # Código fuente React
│   ├── public/              # Assets estáticos
│   └── package.json         # Dependencias de Node
└── uploads/                 # Almacenamiento temporal de archivos (ignorado en git)
```

## ⚙️ Instalación y Configuración

### Backend
1. Crear entorno virtual: `python -m venv .venv`
2. Instalar dependencias: `pip install -r backend/requirements.txt`
3. Ejecutar: `uvicorn main:app --reload` (dentro de la carpeta backend)

### Frontend
1. Instalar dependencias: `npm install`
2. Configurar `.env` con la URL de la API: `VITE_API_URL=http://localhost:8000/api`
3. Ejecutar: `npm run dev`

## ☁️ Despliegue (Render)

El proyecto está configurado para despliegue automático en Render:
- **Backend**: Utiliza el `Procfile` y `runtime.txt`.
- **Frontend**: Requiere la variable de entorno `VITE_API_URL` apuntando al servicio de backend.

---
*Desarrollado con enfoque en precisión técnica y experiencia de usuario.*
