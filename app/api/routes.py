from fastapi import APIRouter, HTTPException, Depends
from app.core.ai_engine import get_guro_response, get_guro_response_stream, personas, guro_graph, GuroState
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Persona, ChatMessage

router = APIRouter()

# Schema for adding/updating personas
class PersonaUpdate(BaseModel):
    grade_level: str
    description: str

# 1. Initialize a global list to store the conversation
# For a TV system, we'll keep this lightweight
chat_history = [] 

@router.get("/ask")
async def ask_guro(query: str, grade: str = "Grade 7", db: Session = Depends(get_db)):
    # Now you can query the DB for the persona
    persona_entry = db.query(Persona).filter(Persona.grade_level == grade).first()
    persona_desc = persona_entry.description if persona_entry else "Mentor vibe..."
    
    # Use the retrieved description for your AI engine
    raw_answer = await get_guro_response(query, chat_history, grade)
    
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
async def list_personas(db: Session = Depends(get_db)):
    # This query triggers the database connection and file creation
    db_personas = db.query(Persona).all()
    return {p.grade_level: p.description for p in db_personas}

# DELETE: Remove a grade level
@router.delete("/personas/{grade_level}")
async def delete_persona(grade_level: str):
    if grade_level in personas:
        del personas[grade_level]
        return {"message": f"Deleted {grade_level}"}
    raise HTTPException(status_code=404, detail="Grade level not found")


@router.get("/ask/graph")
async def ask_guro_graph(query: str, grade: str = "Grade 7", db: Session = Depends(get_db)):
    # 1. Fetch persistent history from DB (Last 6 messages for sliding window)
    db_history = db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).limit(6).all()
    formatted_history = [(msg.role, msg.content) for msg in reversed(db_history)]

    # 2. Initialize state with the user-provided grade (e.g., "TVET")
    initial_state: GuroState = {
        "question": query,
        "grade": grade,
        "history": formatted_history,
        "response": ""
    }
    
    # 3. Invoke the LangGraph workflow
    result = await guro_graph.ainvoke(initial_state)
    answer = result.get("response", "Pasensya na, I couldn't generate an answer.")
    
    # 4. Persist the new turn to the database
    db.add_all([
        ChatMessage(role="human", content=query),
        ChatMessage(role="ai", content=answer)
    ])
    db.commit()
        
    return {
        "status": "success",
        "engine": "LangGraph with SQLite Persistence",
        "answer": answer
    }