import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from app.core.config import OLLAMA_BASE_URL

# Setup Embeddings using local Ollama instance
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_BASE_URL
)

# Persistence path for the FAISS index
DB_FAISS_PATH = "/app/data/vectorstore/db_faiss"

def create_vector_store(texts: list[str]):
    """Converts raw strings into a FAISS vector index."""
    docs = [Document(page_content=t) for t in texts]
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)
    vectorstore.save_local(DB_FAISS_PATH)
    return vectorstore

def get_vector_store():
    """Loads the existing vector store from disk."""
    if os.path.exists(DB_FAISS_PATH):
        # allow_dangerous_deserialization is required for local FAISS loads
        return FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    return None