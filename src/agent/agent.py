"""Define the agent Finbot"""
from typing import List

from langchain_core.language_models import BaseLanguageModel
from langchain_core.vectorstores import VectorStore
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent

from src.settings.config import settings

from src.agent.prompts import AGENT_SYSTEM_PROMPT
from src.rag.vectorstore import create_rag_tool
from src.tools.financial_api import create_financial_api_tool
from src.tools.financial_calc import create_financial_calculator_tool

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

    rag_tool = create_rag_tool(vectorstore)
    financial_api_tool = create_financial_api_tool()
    calculator_tool = create_financial_calculator_tool()

    tools: List[BaseTool] = [
        rag_tool,
        financial_api_tool,
        calculator_tool,
    ]

    # prompt_template = PromptTemplate.from_template(AGENT_SYSTEM_PROMPT)
    # prompt = prompt_template.partial(
    # tool_names=", ".join([tool.name for tool in tools])
    # )

    prompt = PromptTemplate.from_template(
        template=AGENT_SYSTEM_PROMPT
    )

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )
    return agent_executor


def query_agent(agent: AgentExecutor, query:str) -> str:
    """
    Executes a query on the agent.

    Args:
        agent: The agent to query
        query: The user's query

    Returns:
        Dict: Query result
    """
    try:
        response = agent.invoke({"input": query})
        return {
            "success": True,
            "response": response["output"],
            "thought_process": response.get("intermediate_steps", [])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "Lo siento, no pude procesar tu consulta. Por favor, intenta nuevamente."
        }
