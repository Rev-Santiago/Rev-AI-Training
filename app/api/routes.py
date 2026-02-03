from fastapi import APIRouter
from app.core.ai_engine import get_guro_response

router = APIRouter()

@router.get("/ask")
async def ask_guro(query: str):
    raw_answer = await get_guro_response(query)
    
    # 2. LIST COMPREHENSION: Clean and filter the output
    # This removes markdown characters and keeps only titled words
    keywords = [
        word.strip("*").strip(":") 
        for word in raw_answer.split() 
        if word.strip("*").strip(":").istitle() and word.strip("*").strip(":").isalpha()
    ]
    
    # 3. STRUCTURED DATA: Organize the response into a Dictionary
    structured_data = {
        "status": "success",
        "metadata": {
            "model": "gemma3:4b",
            "assistant": "Guro",
            "keyword_count": len(keywords)
        },
        "content": {
            "answer": raw_answer,
            "extracted_keywords": keywords
        }
    }
    
    # 4. Return the dictionary (FastAPI automatically converts this to JSON)
    return structured_data