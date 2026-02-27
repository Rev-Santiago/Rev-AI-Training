from langchain_ollama import ChatOllama 
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.core.config import MODEL_NAME, OLLAMA_BASE_URL
from typing import AsyncGenerator, TypedDict, List, Annotated
import psutil
from app.models import Persona
from app.core.database import SessionLocal
from app.core.rag_engine import get_vector_store
from langgraph.graph.message import add_messages

# 1. Configuration & LLM Setup
# Using ChatOllama to enable .bind_tools() functionality
llm = ChatOllama(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    num_predict=1536, 
    temperature=0.75  
)

# 2. Initialize Free Tools
# Explicitly initialize the wrapper to help resolve Pylance ghost redlines
api_wrapper = WikipediaAPIWrapper(wiki_client= None) 
wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
search = DuckDuckGoSearchRun()

# 3. Custom Tool: Refactored RAG Logic
@tool
def search_local_documents(query: str):
    """Searches local PDF and TXT documents for specific course information."""
    vectorstore = get_vector_store() # References your rag_engine.py
    if not vectorstore:
        return "No local documents found."
    # Preserves your existing similarity search implementation
    docs = vectorstore.similarity_search(query, k=2)
    return "\n\n".join([doc.page_content for doc in docs])

# Register all tools for the agent
tools = [wikipedia, search, search_local_documents]
llm_with_tools = llm.bind_tools(tools)

# 4. Agentic State Definition
class GuroState(TypedDict):
    question: str
    grade: str
    history: List
    messages: Annotated[list, add_messages] # ToolNode looks for this by default
    context: str
    response: str # Add this to resolve the 'defined key' redline

# 5. Helper Functions
def get_persona_from_db(grade: str):
    """Fetches persona from guro.db using the Database Factory"""
    db = SessionLocal()
    try:
        result = db.query(Persona).filter(Persona.grade_level == grade).first()
        if result: return result.description
        fallback = db.query(Persona).filter(Persona.grade_level == "Grade 7").first()
        return fallback.description if fallback else "You are a helpful Filipino teacher."
    finally:
        db.close()

def check_system_resources():
    """Resource monitoring using psutil"""
    vm = psutil.virtual_memory()
    return (True, "Healthy") if vm.percent <= 90 else (False, f"Server Load High: {vm.percent}%")

# 6. Agent Nodes & Logic
async def call_guro_agent(state: GuroState):
    persona = get_persona_from_db(state['grade'])
    system_message = SystemMessage(content=f"You are Guro, a Filipino teacher. {persona}. Use tools for facts or weather.")
    messages = [system_message] + state['history'] + [HumanMessage(content=state['question'])]
    res = await llm_with_tools.ainvoke(messages)
    return {"response": [res]}

def should_continue(state: GuroState):
    # This now checks the 'messages' key, resolving your redline
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "action"
    return END

# 7. Agentic Graph Construction
workflow = StateGraph(GuroState)
workflow.add_node("agent", call_guro_agent)
workflow.add_node("action", ToolNode(tools))
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("action", "agent")
guro_graph = workflow.compile()

# 8. API Integration Functions
async def get_guro_response(user_input: str, chat_history: list, grade: str = "Grade 7"):
    # Initialize the state using the 'messages' key instead of 'response'
    state: GuroState = {
        "question": user_input, 
        "grade": grade, 
        "history": chat_history, 
        "messages": [], # This matches the updated GuroState
        "context": "",
        "response": ""
    }
    
    # Invoke the graph
    result = await guro_graph.ainvoke(state)
    
    # Access the last message content from the 'messages' list
    return result["messages"][-1].content

async def get_guro_response_stream(user_input: str, chat_history: list, grade: str = "Grade 7") -> AsyncGenerator[str, None]:
    is_healthy, _ = check_system_resources()
    if not is_healthy:
        yield "Pasensya na, the server is busy at the moment."
        return

    # Use .astream() and yield the content string of each chunk
    async for chunk in llm.astream(user_input):
        # Extract only the text content string
        if hasattr(chunk, 'content') and chunk.content:
            yield str(chunk.content)