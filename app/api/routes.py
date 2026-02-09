from fastapi import APIRouter, HTTPException
from app.core.ai_engine import get_guro_response, get_guro_response_stream, personas, guro_graph, GuroState
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

# Schema for adding/updating personas
class PersonaUpdate(BaseModel):
    grade_level: str
    description: str

# 1. Initialize a global list to store the conversation
# For a TV system, we'll keep this lightweight
chat_history = [] 

@router.get("/ask")
async def ask_guro(query: str):
    # Pass BOTH query and chat_history to the graph-powered bridge
    raw_answer = await get_guro_response(query, chat_history)
    
    # Update the history so Guro remembers the next question
    chat_history.append(("human", query))
    chat_history.append(("ai", raw_answer))
    
    # Sliding Window: Keep only the last 3 exchanges (6 items)
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
async def ask_guro_streaming(query: str, grade: str = "Grade 7"):
    # Pass the 'grade' from the URL to the legacy streaming engine
    return StreamingResponse(
        get_guro_response_stream(query, chat_history, grade), 
        media_type="text/plain"
    )

# CREATE & UPDATE: Add or modify a grade level
@router.post("/personas")
async def save_persona(data: PersonaUpdate):
    personas[data.grade_level] = data.description
    return {"message": f"Successfully saved {data.grade_level}", "current_total": len(personas)}

# READ: List all available grade levels
@router.get("/personas")
async def list_personas():
    return personas

# DELETE: Remove a grade level
@router.delete("/personas/{grade_level}")
async def delete_persona(grade_level: str):
    if grade_level in personas:
        del personas[grade_level]
        return {"message": f"Deleted {grade_level}"}
    raise HTTPException(status_code=404, detail="Grade level not found")

# NEW: LangGraph exploration endpoint
@router.get("/ask/graph")
async def ask_guro_graph(query: str, grade: str = "Grade 7"):
    """
    Experimental route using LangGraph to process the request.
    """
    # Explicitly typing this as GuroState removes the red line in the IDE
    initial_state: GuroState = {
        "question": query,
        "grade": grade,
        "history": chat_history,
        "response": ""
    }
    
    # Invoke the graph
    result = await guro_graph.ainvoke(initial_state)
    
    # Extract the response from the updated state
    answer = result.get("response", "Pasensya na, I couldn't generate an answer.")
    
    # Update the global history for the next turn
    chat_history.append(("human", query))
    chat_history.append(("ai", answer))
    
    if len(chat_history) > 6:
        del chat_history[:2]
        
    return {
        "status": "success",
        "engine": "LangGraph Direct",
        "answer": answer
    }