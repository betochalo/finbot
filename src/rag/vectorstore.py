"""Functions for the vectorstore"""
import os
from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.tools import Tool
from langchain_core.retrievers import BaseRetriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.settings.config import settings
from src.agent.prompts import RAG_PROMPT_TEMPLATE
from src.rag.ingestion import load_documents, get_document_count

def get_embeddings() -> Embeddings:
    """
    Initialize and return the embedding model to use for the vectorstore.
    """
    if settings.EMBEDDINGS_PROVIDER == "local":
        model_name = settings.SENTENCE_TRANSFORMER_MODEL
        model_kwargs = {'device': 'cpu'}
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs
            )
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDINGS_MODEL
    )

def get_vectorstore() -> VectorStore:
    """
    Initialize and loader the vectorstore
    If the vectorbase is not, create it with documents of examples.
    Returns:
        VectorStore: Initialized vectorstore
    """
    vectorstore_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "vectorstore"
    )

    os.makedirs(vectorstore_path, exist_ok=True)

    embeddings = get_embeddings()

    if os.path.exists(vectorstore_path) and get_document_count(vectorstore_path) > 0:
        return Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embeddings
        )


    documents = load_documents()

    if not documents:
        raise ValueError("No se encontraron documentos para cargar en la base vectorial")

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=vectorstore_path
    )
    vectorstore.persist()
    return vectorstore

def create_rag_tool(
        vectorstore: VectorStore,
        llm: Optional[BaseLanguageModel] = None
) -> Tool:
    """
    Create a tool to query the RAG database.
    Args:
        vectorstore: Vector database for queries
        lm: Optional language model
    Returns:
        Tool: RAG Question Tool
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["question", "context"]
    )

    if llm:
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        chain = create_retrieval_chain(retriever, question_answer_chain)
        return Tool(
            name="financial_knowledge_base",
            description=(
                "Útil para responder preguntas sobre conceptos financieros, "
                "definiciones, principios de inversión, fundamentos del mercado, "
                "de valore y conocimiento financiero general. Usa esta herramienta "
                " cuando necesites información general o explicaciones conceptuales."
            ),
            func=chain.invoke
        )

    return Tool(
        name="financial_knowledge_base",
        description=(
            "Útil para responder preguntas sobre conceptos financieros, "
            "definiciones, principios de inversión, fundamentos del mercado, "
            "de valore y conocimiento financiero general. Usa esta herramienta "
            " cuando necesites información general o explicaciones conceptuales."
        ),
        func=lambda query: retrieve_and_format(retriever, query)
    )

def retrieve_and_format(retriever: BaseRetriever, query: str) -> str:
    """
    Retrieves relevant documents and formats them for use.

    Args:
        retriever: Document retriever
        query: Query to retrieve documents

    Returns:
        str: Documents formatted as context
    """
    docs = retriever.get_relevant_documents(query)

    if not docs:
        return "No se encontró información relevante en la base de conocimiento."

    context = "\n\n".join([
        f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)
    ])
    return context
