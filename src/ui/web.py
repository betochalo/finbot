"""
Interfaz web basada en Streamlit para el agente financiero.
"""
import streamlit as st
from langchain.agents import AgentExecutor

from src.agent.agent import query_agent


def initialize_session_state():
    """Inicializa el estado de la sesión si no existe."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False


def display_chat_history():
    """Muestra el historial de chat."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def add_message(role: str, content: str):
    """
    Añade un mensaje al historial.
    
    Args:
        role: Rol del mensaje ('user' o 'assistant')
        content: Contenido del mensaje
    """
    st.session_state.messages.append({"role": role, "content": content})


def run_web(agent1: AgentExecutor):
    """
    Ejecuta la interfaz web.
    
    Args:
        agent1: Agente a consultar
    """
    st.set_page_config(
        page_title="FinBot - Asistente de Análisis Financiero",
        page_icon="📊",
        layout="wide"
    )


    initialize_session_state()

    with st.sidebar:
        st.title("📊 FinBot")
        st.subheader("Asistente de Análisis Financiero")

        st.markdown("""
        Este asistente te ayuda con:
        * Información financiera general
        * Datos de empresas en bolsa
        * Cálculos financieros
        """)

        st.subheader("Ejemplos de consultas")
        example_queries = [
            "¿Qué es el ratio P/E?",
            "Muéstrame información sobre AAPL",
            "Calcula el ROI de una inversión de $1000 que ahora vale $1500",
            "¿Cuál es el historial de precios de MSFT en el último mes?",
            "Calcula el pago mensual de un préstamo de $10000 al 5% a 3 años"
        ]

        for query in example_queries:
            if st.button(query, key=f"btn_{hash(query)}"):
                add_message("user", query)
                st.session_state.pending_query = query

        st.session_state.debug_mode = st.checkbox(
            "Modo debug (muestra proceso de pensamiento)",
            value=st.session_state.debug_mode
        )

        st.divider()
        st.caption("Desarrollado con LangChain y Streamlit")

    st.title("FinBot - Asistente de Análisis Financiero")

    display_chat_history()

    if hasattr(st.session_state, 'pending_query') and st.session_state.pending_query:
        query = st.session_state.pending_query
        st.session_state.pending_query = None

        with st.spinner("Pensando..."):
            response = query_agent(agent1, query)

        add_message("assistant", response["response"])

        if st.session_state.debug_mode and "thought_process" in response and response["thought_process"]:
            with st.expander("Proceso de pensamiento"):
                for i, step in enumerate(response["thought_process"]):
                    st.write(f"**Paso {i+1}:**")

                    if hasattr(step[0], "tool") and hasattr(step[0], "tool_input"):
                        st.code(f"Herramienta: {step[0].tool}\nEntrada: {step[0].tool_input}")

                    if len(step) > 1:
                        st.write("**Resultado:**")
                        st.text(step[1])

        st.rerun()

    prompt = st.chat_input("¿En qué puedo ayudarte hoy?")

    if prompt:
        add_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = query_agent(agent1, prompt)

            st.markdown(response["response"])

            if st.session_state.debug_mode and "thought_process" in response and response["thought_process"]:
                with st.expander("Proceso de pensamiento"):
                    for i, step in enumerate(response["thought_process"]):
                        st.write(f"**Paso {i+1}:**")

                        if hasattr(step[0], "tool") and hasattr(step[0], "tool_input"):
                            st.code(f"Herramienta: {step[0].tool}\nEntrada: {step[0].tool_input}")

                        if len(step) > 1:
                            st.write("**Resultado:**")
                            st.text(step[1])

        add_message("assistant", response["response"])


if __name__ == "__main__":
    from src.agent.agent import create_agent
    from src.rag.vectorstore import get_vectorstore

    st.write("Inicializando agente...")
    vectorstore = get_vectorstore()
    agent = create_agent(vectorstore)
    run_web(agent)
