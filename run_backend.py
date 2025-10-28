#!/usr/bin/env python
"""
Script para iniciar o servidor backend
"""
import subprocess
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from src.config import BACKEND_PORT, DEBUG

if __name__ == "__main__":
    print(f"🚀 Iniciando backend na porta {BACKEND_PORT}...")
    print(f"📍 Acesse: http://localhost:{BACKEND_PORT}")
    print(f"📚 Documentação: http://localhost:{BACKEND_PORT}/docs")
    
    try:
        subprocess.run([
            sys.executable,
            "src/backend/main.py"
        ])
    except KeyboardInterrupt:
        print("\n✋ Servidor encerrado")