from fastapi import APIRouter
from app.core.ai_engine import get_guro_response, get_guro_response_stream
from fastapi.responses import StreamingResponse

router = APIRouter()

# 1. Initialize a global list to store the conversation
# For a TV system, we'll keep this lightweight
chat_history = [] 

@router.get("/ask")
async def ask_guro(query: str):
    # 2. Pass BOTH query and chat_history to fix the TypeError
    raw_answer = await get_guro_response(query, chat_history)
    
    # 3. Update the history so Guro remembers the next question
    chat_history.append(("human", query))
    chat_history.append(("ai", raw_answer))
    
    # 4. Sliding Window: Keep only the last 3 exchanges (6 items)
    # This protects the TV's limited RAM from filling up
    if len(chat_history) > 6:
        del chat_history[:2] 

    return {
        "status": "success",
        "metadata": {
            "model": "gemma3:4b",
            "assistant": "Guro"
        },
        "content": {
            "answer": raw_answer
        }
    }

@router.get("/ask/stream")
async def ask_guro_streaming(query: str, grade: str = "Grade 1"):
    # Pass the 'grade' from the URL to the engine
    return StreamingResponse(
        get_guro_response_stream(query, chat_history, grade), 
        media_type="text/plain"
    )