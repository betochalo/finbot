"""Define the agent Finbot"""
from src.settings.config import settings

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.vectorstores import VectorStore
from langchain_openai import ChatOpenAI


def get_llm() -> BaseLanguageModel:
    """
    Initialize and return the LLM model to use for the agent.
    """
    return ChatOpenAI(
        model=settings.MODEL_PROVIDER,
        temperature=0,
        api_key=settings.OPENAI_API_KEY,
    )

def create_agent(vectorstore: VectorStore) -> AgentExecutor:
    """
    Create and set up the agent with its tools

    Args:
        vectorstore: Vectorial Base for RAG search
    
    Returns:
        AgentExecutor: Executor for the agent
    """
    llm = get_llm()

    