"""
FinBot - Asistente de Análisis de Datos Financieros
Un agente de IA que utiliza RAG y herramientas financieras para responder preguntas.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import create_agent
from src.rag.vectorstore import get_vectorstore
from src.ui.web import run_web


def main():
    """Punto de entrada principal de la aplicación."""
    print("Inicializando FinBot - Asistente de Análisis Financiero...")

    vectorstore = get_vectorstore()

    agent = create_agent(vectorstore)

    print("Iniciando interfaz web...")
    run_web(agent)

if __name__ == "__main__":
    main()
