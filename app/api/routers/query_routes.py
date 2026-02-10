from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Persona, ChatMessage
from app.core.ai_engine import get_guro_response, get_guro_response_stream, guro_graph, GuroState

router = APIRouter(prefix="/ask", tags=["Queries"])
chat_history = [] # For legacy/in-memory testing

@router.get("/")
async def ask_guro(query: str, grade: str = "Grade 7", db: Session = Depends(get_db)):
    # Query the DB for the persona to ensure persistence
    persona_entry = db.query(Persona).filter(Persona.grade_level == grade).first()
    persona_desc = persona_entry.description if persona_entry else "Mentor vibe..."
    
    raw_answer = await get_guro_response(query, chat_history, grade)
    
    chat_history.append(("human", query))
    chat_history.append(("ai", raw_answer))
    
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


@router.get("/stream")
async def ask_guro_streaming(query: str, grade: str = "Grade 7"):
    return StreamingResponse(get_guro_response_stream(query, chat_history, grade), media_type="text/plain")

@router.get("/graph")
async def ask_guro_graph(query: str, grade: str = "Grade 7", db: Session = Depends(get_db)):
    # 1. Fetch persistent history from DB (Last 6 messages)
    db_history = db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).limit(6).all()
    formatted_history = [(msg.role, msg.content) for msg in reversed(db_history)]

    # 2. Initialize state with the user-provided grade
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