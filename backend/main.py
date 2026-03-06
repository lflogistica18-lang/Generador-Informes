"""
main.py — FastAPI entry point para el Generador de Informes MIP
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routers import upload, reports, clients
import config

app = FastAPI(
    title=config.APP_TITLE,
    description="API para parsear PDFs de visitas y generar Informes MIP Mensuales",
    version=config.APP_VERSION,
)

# CORS — permitir requests desde el frontend
origins = config.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False, # Ponemos False para que funcione con '*' mientras probamos
    allow_methods=["*"],
    allow_headers=["*"],
)


# Servir imágenes estáticas extraídas de los PDFs para que el frontend pueda mostrarlas
if os.path.exists(config.IMAGES_DIR):
    app.mount("/static/images", StaticFiles(directory=config.IMAGES_DIR), name="images")

# Routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Generador Informes MIP"}

if __name__ == "__main__":
    import uvicorn
    print(f"Iniciando servidor en http://localhost:8000")
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"Error al iniciar uvicorn: {e}")
