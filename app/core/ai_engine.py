from langchain_ollama import OllamaLLM 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import MODEL_NAME, OLLAMA_BASE_URL
from typing import Annotated, TypedDict, List, Union
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.models import Persona
import psutil

# 1. Configuration & LLM Setup
llm = OllamaLLM(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    num_predict=1536, 
    temperature=0.75  
)

# 2. CRUD-able Personas
personas = {
    "Grade 1": "Persona for 6-year-olds: Use very simple words, many emojis, and short sentences. Analogies: Toys and snacks.",
    "Grade 2": "Persona for 7-year-olds: Simple words but introduce basic 'How' and 'Why'. Analogies: Animals and nature.",
    "Grade 3": "Persona for 8-year-olds: Conversational Taglish. Focus on storytelling and curiosity. Analogies: Superheroes and games.",
    "Grade 4": "Persona for 9-year-olds: Balanced English-Tagalog. Use analogies about school and sports.",
    "Grade 5": "Persona for 10-year-olds: Introduce more structured facts and 'Science/History' terms. Analogies: Hobbies and inventions.",
    "Grade 6": "Persona for 11-year-olds: Prepare them for high school. Use critical thinking questions. Analogies: Technology and teamwork.",
    "Grade 7": "Persona for 12-13 year olds: Mentor vibe. Use detailed facts, proper terminology, and social analogies."
}

def get_persona_for_grade(grade: str):
    return personas.get(grade, personas["Grade 7"])  # Default to the most advanced persona if not found

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
    """The main AI node in the graph."""
    # This remains dynamic based on the 'grade' passed in the state
    persona = get_persona_for_grade(state['grade']) 
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are Guro, a Filipino teacher. {persona}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])
    
    chain = prompt | llm
    # history in state is now the list of tuples from the DB
    res = await chain.ainvoke({"question": state['question'], "history": state['history']})
    return {"response": res}

# Building and Compiling the Graph
workflow = StateGraph(GuroState)
workflow.add_node("guro", call_guro_node)
workflow.set_entry_point("guro")
workflow.add_edge("guro", END)

# This MUST be defined before any functions that call it
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
    """Legacy Streaming for A/B comparison"""
    is_healthy, _ = check_system_resources()
    if not is_healthy:
        yield "Pasensya na, the server is busy."
        return

    persona_instruction = get_persona_for_grade(grade)
    system_prompt = f"You are Guro, a legendary Filipino teacher. {persona_instruction}"

    dynamic_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = dynamic_prompt | llm
    async for chunk in chain.astream({"question": user_input, "history": chat_history}):
        yield chunk

def get_persona_from_db(db: Session, grade: str):
    """Replaces the dictionary lookup with a DB query"""
    result = db.query(Persona).filter(Persona.grade_level == grade).first()
    if result:
        return result.description
    # Fallback to Grade 7 if TVET or others aren't found
    fallback = db.query(Persona).filter(Persona.grade_level == "Grade 7").first()
    return fallback.description if fallback else "You are a helpful teacher."