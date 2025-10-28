"""
Configurações do aplicativo Doc Extractor
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

# Criar diretórios se não existirem
for directory in [UPLOAD_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Configurações do Servidor
APP_PORT = int(os.getenv("APP_PORT", 35001))
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 35000))

# Limites de Upload
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 10))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Provider padrão
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "claude")

# Configuração de Logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

# Configuração de Processamento
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 300))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# Modo de desenvolvimento
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Tipos de arquivo permitidos
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

# Layouts CSV
LAYOUT_FILES = {
    "nascimento": DATA_DIR / "layout_nascimento.csv",
    "casamento": DATA_DIR / "layout_casamento.csv",
    "obito": DATA_DIR / "layout_obito.csv"
}

# Configurações de API (não armazenar chaves aqui)
API_PROVIDERS = {
    "claude": {
        "name": "Anthropic Claude",
        "model": "claude-3-7-sonnet-20241022",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "max_tokens": 4096
    },
    "gemini": {
        "name": "Google Gemini",
        "model": "gemini-2.0-flash", 
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "max_tokens": 8192
    }
}