"""Functions for the vectorstore"""
import os

from src.settings.config import settings

from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from src.rag.ingestion import get_document_count


def get_embeddings() -> Embeddings:
    """
    Initialize and return the embedding model to use for the vectorstore.
    """
    if settings.EMBEDDINGS_PROVIDER == "local":
        model_name = settings.SENTENCE_TRANSFORMER_MODEL
        return HuggingFaceEmbeddings(model_name=model_name)
    else:
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
    
    from src.rag.ingestion import load_documents
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




