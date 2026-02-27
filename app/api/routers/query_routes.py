from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Persona, ChatMessage
from app.core.ai_engine import get_guro_response, get_guro_response_stream, guro_graph, GuroState
from langchain_core.messages import HumanMessage

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
    # Return the generator directly
    return StreamingResponse(
        get_guro_response_stream(query, chat_history, grade), 
        media_type="text/plain"
    )

@router.get("/graph")
async def ask_guro_graph(query: str, session_id: str, grade: str = "Grade 7", db: Session = Depends(get_db)):
    # 1. Fetch persistent history from DB
    db_history = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session_id)\
        .order_by(ChatMessage.timestamp.desc())\
        .limit(6).all()
        
    # Format for LangGraph's history list
    formatted_history = [(msg.role, msg.content) for msg in reversed(db_history)]

    # 2. Initialize state with 'messages' key to resolve Pylance redline
    # We pass the user query as a HumanMessage object inside the 'messages' list
    initial_state: GuroState = {
        "question": query,
        "grade": grade,
        "history": formatted_history,
        "context": "",
        "messages": [HumanMessage(content=query)], # This allows ToolNode to "see" the intent
        "response": ""
    }
    
    # 3. Invoke the Agentic Graph
    result = await guro_graph.ainvoke(initial_state)
    
    # 4. Extract result from the message sequence
    # LangGraph returns the full message list; the last one is the Guro answer
    final_msg = result["messages"][-1]
    answer = final_msg.content if hasattr(final_msg, 'content') else "Pasensya na, I couldn't generate an answer."
    
    # 5. Persistence: Save new messages to maintain session isolation
    db.add_all([
        ChatMessage(role="human", content=query, session_id=session_id),
        ChatMessage(role="ai", content=answer, session_id=session_id)
    ])
    db.commit()
        
    return {
        "status": "success",
        "session_id": session_id,
        "answer": answer
    }