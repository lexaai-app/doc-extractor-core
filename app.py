"""
Frontend Streamlit para Doc Extractor
"""
import streamlit as st
import requests
import json
from pathlib import Path
import base64
import sys

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import (
    APP_PORT, BACKEND_PORT, MAX_FILE_SIZE_MB,
    ALLOWED_EXTENSIONS, DEFAULT_PROVIDER
)

# Configuração da página
st.set_page_config(
    page_title="Doc Extractor - Extração Inteligente de Documentos",
    page_icon="📄",
    layout="wide"
)

# URL do backend
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"

# Estilos CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stAlert {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .upload-area {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📄 Doc Extractor</h1>
    <p>Extração Inteligente de Documentos com IA</p>
</div>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'provider' not in st.session_state:
    st.session_state.provider = DEFAULT_PROVIDER

# Sidebar para configuração
with st.sidebar:
    st.header("⚙️ Configuração")
    
    # Seleção do Provider
    provider = st.selectbox(
        "Provider de IA",
        options=["claude", "gemini"],
        index=0 if DEFAULT_PROVIDER == "claude" else 1,
        help="Escolha o modelo de IA para extração"
    )
    st.session_state.provider = provider
    
    # API Key
    api_key = st.text_input(
        "API Key",
        type="password",
        value=st.session_state.api_key,
        help="Sua chave de API (não será armazenada)"
    )
    st.session_state.api_key = api_key
    
    # Tipo de extração
    extraction_type = st.radio(
        "Tipo de Extração",
        options=["basic", "advanced"],
        format_func=lambda x: "Básica (Documento Único)" if x == "basic" else "Avançada (Múltiplos Documentos)",
        help="Básica: RG, CPF, CNH | Avançada: PDFs com múltiplos documentos"
    )
    
    # Para extração avançada
    document_type = None
    if extraction_type == "advanced":
        document_type = st.selectbox(
            "Tipo de Registro",
            options=["nascimento", "casamento", "obito"],
            format_func=lambda x: x.capitalize()
        )
    
    # Modo de operação
    mode = st.radio(
        "Modo de Operação",
        options=["automatic", "manual"],
        format_func=lambda x: "Automático com IA" if x == "automatic" else "Manual",
        help="Automático: IA extrai os dados | Manual: Você preenche os campos"
    )
    
    # Status do Backend
    st.divider()
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend conectado")
        else:
            st.error("❌ Backend não respondendo")
    except:
        st.error("❌ Backend offline")

# Área principal
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload de Documento")
    
    # Validação antes do upload
    if not api_key:
        st.warning("⚠️ Por favor, configure sua API Key na barra lateral")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Arraste ou selecione seu documento",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        help=f"Tamanho máximo: {MAX_FILE_SIZE_MB}MB"
    )
    
    if uploaded_file is not None:
        # Validar tamanho
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"❌ Arquivo muito grande! Máximo: {MAX_FILE_SIZE_MB}MB")
        else:
            st.success(f"✅ Arquivo carregado: {uploaded_file.name} ({file_size_mb:.2f}MB)")
            
            # Preview para imagens
            if uploaded_file.type in ["image/jpeg", "image/png", "image/jpg"]:
                st.image(uploaded_file, caption="Preview do documento", use_column_width=True)
            
            # Botão de processar
            if st.button("🚀 Processar Documento", disabled=not api_key, type="primary"):
                with st.spinner("Processando..."):
                    try:
                        # Preparar dados para envio
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {
                            "provider": provider,
                            "api_key": api_key,
                            "extraction_type": extraction_type,
                            "document_type": document_type,
                            "mode": mode
                        }
                        
                        # Fazer requisição
                        response = requests.post(
                            f"{BACKEND_URL}/api/extract",
                            files=files,
                            data=data,
                            timeout=300
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.extraction_result = result
                            st.success("✅ Documento processado com sucesso!")
                        else:
                            st.error(f"❌ Erro: {response.text}")
                            
                    except Exception as e:
                        st.error(f"❌ Erro na comunicação: {str(e)}")

with col2:
    st.header("📋 Resultados da Extração")
    
    if 'extraction_result' in st.session_state:
        result = st.session_state.extraction_result
        
        # Mostrar status
        st.info(f"Provider: {result.get('provider', 'N/A')}")
        st.info(f"Tipo de Extração: {result.get('extraction_type', 'N/A')}")
        
        # Mostrar dados extraídos (por enquanto mock)
        st.subheader("Dados Extraídos")
        extracted_data = result.get('data', {}).get('extracted_fields', {})
        
        if extracted_data:
            # Mostrar campos em formato editável
            edited_data = {}
            for field, value in extracted_data.items():
                edited_data[field] = st.text_input(field, value=value)
        else:
            st.info("Aguardando processamento...")
        
        # Botões de ação
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("📋 Copiar JSON"):
                json_str = json.dumps(result.get('data', {}), indent=2, ensure_ascii=False)
                st.code(json_str, language="json")
                st.success("✅ Copiado para área de transferência!")
        
        with col_btn2:
            if st.button("📄 Exportar PDF"):
                st.info("🚧 Funcionalidade em desenvolvimento")
        
        with col_btn3:
            if extraction_type == "advanced" and st.button("📝 Exportar XML"):
                st.info("🚧 Funcionalidade em desenvolvimento")
    else:
        st.info("👆 Faça upload de um documento para começar")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Doc Extractor v0.1.0 | Desenvolvido para extração inteligente de documentos</p>
</div>
""", unsafe_allow_html=True)