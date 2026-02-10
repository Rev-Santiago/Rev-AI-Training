from langchain_ollama import OllamaLLM 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import MODEL_NAME, OLLAMA_BASE_URL
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.models import Persona
from app.core.database import SessionLocal  # Import to create temporary sessions
import psutil

# 1. Configuration & LLM Setup
llm = OllamaLLM(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    num_predict=1536, 
    temperature=0.75  
)

# 2. Database-Driven Persona Logic
def get_persona_from_db(grade: str):
    """Fetches persona description from SQLite with a fallback."""
    db = SessionLocal()
    try:
        result = db.query(Persona).filter(Persona.grade_level == grade).first()
        if result:
            return result.description
        
        # Fallback to Grade 7 if the specific grade isn't found
        fallback = db.query(Persona).filter(Persona.grade_level == "Grade 7").first()
        return fallback.description if fallback else "You are a helpful Filipino teacher."
    finally:
        db.close()

# 3. System Health Check
def check_system_resources():
    vm = psutil.virtual_memory()
    if vm.percent > 90:
        return False, f"Server Load High: {vm.percent}%"
    return True, "Healthy"

# 4. LangGraph Implementation
class GuroState(TypedDict):
    question: str
    grade: str
    response: str
    history: List

async def call_guro_node(state: GuroState):
    """The main AI node in the graph using DB-persisted personas."""
    # Logic now pulls directly from the database
    persona = get_persona_from_db(state['grade']) 
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are Guro, a Filipino teacher. {persona}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])
    
    chain = prompt | llm
    res = await chain.ainvoke({"question": state['question'], "history": state['history']})
    return {"response": res}

# Building and Compiling the Graph
workflow = StateGraph(GuroState)
workflow.add_node("guro", call_guro_node)
workflow.set_entry_point("guro")
workflow.add_edge("guro", END)
guro_graph = workflow.compile()

# 5. Response Functions
async def get_guro_response(user_input: str, chat_history: list, grade: str = "Grade 7"):
    """Standard JSON response powered by LangGraph"""
    state: GuroState = {
        "question": user_input,
        "grade": grade, 
        "history": chat_history,
        "response": ""
    }
    result = await guro_graph.ainvoke(state)
    return result["response"]

async def get_guro_response_stream(user_input: str, chat_history: list, grade: str = "Grade 7"):
    """Streaming response using DB-persisted personas"""
    is_healthy, _ = check_system_resources()
    if not is_healthy:
        yield "Pasensya na, the server is busy."
        return

    persona_instruction = get_persona_from_db(grade)
    system_prompt = f"You are Guro, a legendary Filipino teacher. {persona_instruction}"

    dynamic_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = dynamic_prompt | llm
    async for chunk in chain.astream({"question": user_input, "history": chat_history}):
        yield chunk