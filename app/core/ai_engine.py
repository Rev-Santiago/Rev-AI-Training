from langchain_ollama import OllamaLLM 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import MODEL_NAME, OLLAMA_BASE_URL
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.models import Persona
from app.core.database import SessionLocal  # Import to create temporary sessions
import psutil
from app.core.rag_engine import get_vector_store

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
    context: str

# 2. Add Retrieval Node
async def retrieve_context_node(state: GuroState):
    """Searches FAISS for relevant information based on the question."""
    vectorstore = get_vector_store()
    if not vectorstore:
        return {"context": "No local documents found."}
    
    # Retrieve top 2 most relevant chunks
    docs = vectorstore.similarity_search(state['question'], k=2)
    context_text = "\n\n".join([doc.page_content for doc in docs])
    return {"context": context_text}

# 3. Update the LLM Node to use context
async def call_guro_node(state: GuroState):
    persona = get_persona_from_db(state['grade']) 
    
    # Incorporate retrieved context into the system prompt
    system_message = (
        f"You are Guro, a Filipino teacher. {persona}\n\n"
        f"Context from local files:\n{state.get('context', 'None available.')}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])
    
    chain = prompt | llm
    res = await chain.ainvoke({"question": state['question'], "history": state['history']})
    return {"response": res}

# 4. Wire the Node into the Workflow
workflow = StateGraph(GuroState)
workflow.add_node("retrieve", retrieve_context_node) # New node
workflow.add_node("guro", call_guro_node)
workflow.set_entry_point("retrieve") # Start with retrieval
workflow.add_edge("retrieve", "guro") # Then go to AI generation
workflow.add_edge("guro", END)

guro_graph = workflow.compile()

# 5. Response Functions
async def get_guro_response(user_input: str, chat_history: list, grade: str = "Grade 7"):
    """Standard JSON response powered by LangGraph"""
    state: GuroState = {
        "question": user_input,
        "grade": grade, 
        "history": chat_history,
        "context": "",
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