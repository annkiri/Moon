import os
import sys
import time
import warnings

# --- 0. SILENCIAR ADVERTENCIAS ---
warnings.filterwarnings("ignore")

# --- 1. PARCHE DE RUTA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)

# --- 2. IMPORTS ---
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402
from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from src.core.database import Note, SessionLocal, Task, TransactionModel  # noqa: E402
from src.core.graph import app  # noqa: E402

# Configuración de página
st.set_page_config(page_title="Moon AI", page_icon="🌙", layout="wide")


# --- FUNCIONES DE CARGA DE DATOS ---
def get_data(model):
    """Obtiene los últimos 20 registros de la tabla dada."""
    db: Session = SessionLocal()
    try:
        data = db.query(model).order_by(model.id.desc()).limit(20).all()
        return [d.__dict__ for d in data]
    finally:
        db.close()


# --- INTERFAZ PRINCIPAL ---
st.title("🌙 MOON AI")
st.markdown("*Tu asistente personal (Financial & Second Brain)*")

# Creamos Pestañas
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🧠 Cerebro (Data)", "📊 Debug"])

# --- PESTAÑA 1: CHAT ---
with tab1:
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Mostrar historial
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user", avatar="👺"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg.content)

    # Input de usuario
    user_input = st.chat_input("Escribe tu gasto, idea o tarea...")

    if user_input:
        # 1. Mostrar mensaje usuario
        with st.chat_message("user", avatar="👺"):
            st.write(user_input)

        st.session_state.messages.append(HumanMessage(content=user_input))

        # 2. Procesar con Moon
        with st.chat_message("assistant", avatar="🤖"):
            # Placeholder para mostrar que está pensando
            status_placeholder = st.empty()
            status_placeholder.markdown("⏳ *Moon está pensando...*")

            start_total = time.time()

            # Invocamos al grafo
            response = app.invoke({"messages": st.session_state.messages})

            end_total = time.time()
            total_duration = end_total - start_total

            # Limpiamos el texto de "pensando"
            status_placeholder.empty()

            # Mostrar respuesta final
            ai_msg = response["messages"][-1]
            st.write(ai_msg.content)

            # --- SECCIÓN DE TIEMPOS (SIEMPRE VISIBLE) ---
            # Usamos un expander que persiste después de la respuesta
            with st.expander(f"⏱️ Detalles de Ejecución ({total_duration:.2f}s)"):
                if "debug_logs" in response:
                    for log in response["debug_logs"]:
                        st.text(log)  # Usamos st.text para formato monospaced limpio
                else:
                    st.warning("No se recibieron logs de tiempo.")

            st.session_state.messages.append(ai_msg)

# --- PESTAÑA 2: CEREBRO (VISUALIZACIÓN) ---
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Finanzas Recientes")
        data_tx = get_data(TransactionModel)
        if data_tx:
            df_tx = pd.DataFrame(data_tx)
            if "_sa_instance_state" in df_tx.columns:
                del df_tx["_sa_instance_state"]
            st.dataframe(df_tx, width="stretch", hide_index=True)
        else:
            st.info("No hay gastos registrados aún.")

    with col2:
        st.subheader("✅ Tareas Pendientes")
        data_tasks = get_data(Task)
        if data_tasks:
            df_tasks = pd.DataFrame(data_tasks)
            if "_sa_instance_state" in df_tasks.columns:
                del df_tasks["_sa_instance_state"]
            st.dataframe(df_tasks, width="stretch", hide_index=True)
        else:
            st.info("No hay tareas pendientes.")

    st.subheader("📝 Notas & Ideas")
    data_notes = get_data(Note)
    if data_notes:
        df_notes = pd.DataFrame(data_notes)
        if "_sa_instance_state" in df_notes.columns:
            del df_notes["_sa_instance_state"]
        st.dataframe(df_notes, width="stretch", hide_index=True)
    else:
        st.info("Tu mente está vacía (de notas).")

# --- PESTAÑA 3: DEBUG (LOGS) ---
with tab3:
    st.write("Estado de la sesión (Mensajes):")
    st.json([m.content for m in st.session_state.messages])
