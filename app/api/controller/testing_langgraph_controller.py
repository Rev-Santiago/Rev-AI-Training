from fastapi import APIRouter, HTTPException
from app.core.ai_engine import get_guro_response, get_guro_response_stream, personas, guro_graph, GuroState
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()
from app.core.ai_engine import get_guro_response, get_guro_response_stream, personas, guro_graph, GuroState

chat_history = [] 

@router.get("/ask/graph")
async def ask_guro_graph(query: str, grade: str = "Grade 4"):
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