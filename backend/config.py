"""
config.py — Configuración global del backend
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Directorios de datos (En Render usaremos /tmp para datos efímeros 
# o directorios locales que se limpian tras apagar la instancia)
UPLOADS_DIR = os.path.join(ROOT_DIR, "uploads")
OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")
DATA_DIR = os.path.join(ROOT_DIR, "data")
IMAGES_DIR = os.path.join(UPLOADS_DIR, "images")

# Crear directorios si no existen
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Configuración de la app
APP_TITLE = "Generador Informes MIP"
APP_VERSION = "1.0.0"

# CORS: Permitir frontend local y la futura URL de GitHub Pages
# Se puede configurar vía env var frontend_URL en Render
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://lflogistica18-lang.github.io", # Ejemplo de GH Pages
    os.getenv("FRONTEND_URL", "*") # Para ser 100% flexibles al inicio
]

