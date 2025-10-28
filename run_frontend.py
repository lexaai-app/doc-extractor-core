#!/usr/bin/env python
"""
Script para iniciar o frontend Streamlit
"""
import subprocess
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from src.config import APP_PORT

if __name__ == "__main__":
    print(f"🚀 Iniciando frontend na porta {APP_PORT}...")
    print(f"📍 Acesse: http://localhost:{APP_PORT}")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "app.py",
            "--server.port", str(APP_PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n✋ Aplicação encerrada")