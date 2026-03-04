# Generador de Informes MIP — Sanitas Ambiental

App web interna para la generación del **Informe MIP Mensual** consolidado a partir de los informes de visita en PDF.

## Arquitectura

```
/backend    → FastAPI (Python) — Parseo de PDFs, generación de documentos
/frontend   → React + Vite + Tailwind CSS — UI del flujo de carga y generación
```

## Requisitos

- Python 3.12+
- Node.js 18+
- pip / npm

## Instalación y Ejecución

### Backend

```bash
cd backend
pip install -r requirements.txt --user --break-system-packages
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

La app estará disponible en **http://localhost:5173**

## Flujo de Uso

1. Seleccionar cliente, sucursal y mes/año
2. Subir los PDFs del mes (Conformes + MIPs)
3. Revisar y completar datos faltantes
4. Completar el formulario de capturas de voladores
5. Editar los resúmenes de tratamiento
6. Vista previa del informe
7. Descargar en **PDF** y/o **Word (.docx)**

## Estructura de Archivos

```
Generador-Informes/
├── README.md
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt
│   ├── routers/             # Endpoints REST
│   ├── services/            # Lógica de negocio
│   ├── models/              # Schemas Pydantic
│   └── templates/           # HTML para generación de PDF
└── frontend/
    ├── src/
    │   ├── components/      # Componentes reutilizables
    │   ├── pages/           # Vistas del flujo
    │   ├── services/        # API calls
    │   └── store/           # Estado global (Zustand)
    └── public/
```

## Estado del Proyecto (Actualizado 20-02-2026)

### ✅ Mejoras en Generación de Reportes
- **Sistema de Impresión Dinámico**: Implementación de cabeceras y pies de página fijos (`CSS position: fixed`) que se repiten en cada hoja física del PDF.
- **Adaptabilidad según demanda**: El reporte ya no está limitado a 4 páginas fijas; las secciones crecen dinámicamente según la cantidad de desvíos u observaciones.
- **Prevención de cortes**: Reglas de `break-inside: avoid` para asegurar que las tarjetas de fotos y filas de tablas no se corten a mitad de página.
- **Gráficos mejorados**: Agrupación automática de "Otros Sectores" en consumos y gráficos horizontales para mayor legibilidad.

### ✅ Mejoras en Procesamiento
- **Clasificación de Plagas**: Algoritmo unificado para clasificar desvíos fotográficos (Roedores, Voladores, Rastreros) mediante análisis de texto del sector y descripción.
- **Manejo de directorios**: Corrección de bugs de compatibilidad de rutas entre Windows (\) y WSL (/).

---
*Sanitas Ambiental — Excelencia en Control de Plagas*
