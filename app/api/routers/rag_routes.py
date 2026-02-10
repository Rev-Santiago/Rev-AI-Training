from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from pypdf import PdfReader
from app.core.rag_engine import create_vector_store
import io

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Reads a file (PDF or TXT) and indexes it into FAISS."""
    filename = (file.filename or "").lower()
    
    try:
        content = await file.read()
        
        if filename.endswith(".pdf"):
            # Handle PDF Binary
            pdf_reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n\n"
        else:
            # Handle Plain Text
            text = content.decode("utf-8")

        # Basic Chunking
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No extractable text found in file.")

        create_vector_store(chunks)
        
        return {
            "filename": file.filename,
            "chunks_indexed": len(chunks),
            "status": "Success: FAISS index updated."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/query")
async def query_vector_store(prompt: str):
    """
    Endpoint for RAG queries.
    Future logic: Similarity search to retrieve context for the LLM.
    """
    return {
        "query": prompt,
        "results": [],
        "context": "Vector store retrieval logic pending."
    }