"""
Backend API server para Doc Extractor
"""
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import (
    BACKEND_PORT, DEBUG, LOG_LEVEL, ALLOWED_EXTENSIONS, 
    MAX_FILE_SIZE_BYTES
)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Doc Extractor API",
    description="API para extração de dados de documentos usando IA",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ExtractionRequest(BaseModel):
    provider: str
    api_key: str
    extraction_type: str  # "basic" ou "advanced"
    document_type: Optional[str] = None  # Para extração avançada
    mode: str = "automatic"  # "automatic" ou "manual"
    
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str = "0.1.0"

# Rotas
@app.get("/", response_model=HealthResponse)
async def root():
    """Rota raiz - health check"""
    return HealthResponse(
        status="ok",
        message="Doc Extractor API está funcionando"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Serviço operacional"
    )

@app.post("/api/extract")
async def extract_document(
    file: UploadFile = File(...),
    provider: str = Form(...),
    api_key: str = Form(...),
    extraction_type: str = Form(...),
    document_type: Optional[str] = Form(None),
    mode: str = Form("automatic")
):
    """
    Endpoint principal para extração de documentos
    """
    try:
        # Validar arquivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Arquivo não fornecido")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Verificar tamanho
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE_BYTES / 1024 / 1024}MB"
            )
        
        # Validar provider
        if provider not in ["claude", "gemini"]:
            raise HTTPException(
                status_code=400,
                detail="Provider inválido. Use 'claude' ou 'gemini'"
            )
        
        # Por enquanto, retornar uma resposta mock
        # TODO: Implementar a extração real na próxima etapa
        logger.info(f"Processando arquivo: {file.filename} com provider: {provider}")
        
        return JSONResponse(content={
            "status": "success",
            "message": "Extração iniciada",
            "filename": file.filename,
            "provider": provider,
            "extraction_type": extraction_type,
            "document_type": document_type,
            "mode": mode,
            "data": {
                "extracted_fields": {},
                "confidence": 0.0
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na extração: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/layouts")
async def get_layouts():
    """Retorna os tipos de layout disponíveis"""
    return {
        "layouts": ["nascimento", "casamento", "obito"],
        "descriptions": {
            "nascimento": "Registro de Nascimento",
            "casamento": "Registro de Casamento",
            "obito": "Registro de Óbito"
        }
    }

@app.get("/api/providers")
async def get_providers():
    """Retorna os providers de IA disponíveis"""
    return {
        "providers": {
            "claude": {
                "name": "Anthropic Claude",
                "model": "claude-3-7-sonnet"
            },
            "gemini": {
                "name": "Google Gemini",
                "model": "gemini-2.0-flash"
            }
        }
    }

if __name__ == "__main__":
    logger.info(f"Iniciando servidor na porta {BACKEND_PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=BACKEND_PORT,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )