import sys
import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Ajuste de path para importar módulos internos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.graph import app

# Configuración de página
st.set_page_config(page_title="Moon AI", page_icon="🌙", layout="centered")

# Cargar entorno
load_dotenv()

# Título y Estilo
st.title("🌙 Moon AI")
st.caption("Tu asistente financiero personal (Self-hosted)")

# --- GESTIÓN DEL ESTADO (MEMORIA VISUAL) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de chat en la interfaz
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DEL CHAT ---
async def get_response(user_input):
    """Comunicación asíncrona con el Grafo de Moon"""
    input_message = {"messages": [HumanMessage(content=user_input)]}
    
    # Invocamos al grafo
    response = await app.ainvoke(input_message)
    
    # Extraemos el último mensaje del agente
    return response["messages"][-1].content

# Input del usuario
if prompt := st.chat_input("Escribe tu gasto o saluda..."):
    # 1. Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Obtener respuesta de Moon
    with st.chat_message("assistant"):
        with st.spinner("Moon está pensando..."):
            # Streamlit requiere un loop para async
            response_text = asyncio.run(get_response(prompt))
            st.markdown(response_text)
    
    # 3. Guardar respuesta en historial
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- SIDEBAR (DEBUG) ---
with st.sidebar:
    st.header("Debug Info")
    if st.button("Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()
    st.info("Base de datos: SQLite (finance.db)")