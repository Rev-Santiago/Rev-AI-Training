from langchain_ollama import OllamaLLM 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import MODEL_NAME, OLLAMA_BASE_URL
import psutil

# We add 'base_url' if the server is a different machine than the TV
# But for now, leave it as default if testing on your laptop
llm = OllamaLLM(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    num_predict=1536, # Increased from 1024 to give more room for the recap
    temperature=0.75  # Slightly lower to keep it more focused on the facts
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are Guro, a warm and inspiring Filipino teacher. 
    Speak in natural, conversational Taglish (the way teachers actually talk in class). 
    Avoid awkward direct translations. If a term is emotional, use the Tagalog equivalent naturally.
    Always finish your lessons with a clear conclusion and a 'Guro check-in' question."""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

def check_system_resources():
    # Now this monitors the SERVER'S health, not the TV's.
    vm = psutil.virtual_memory()
    if vm.percent > 90:
        return False, f"Server Load High: {vm.percent}%"
    return True, "Healthy"

async def get_guro_response(user_input: str, chat_history: list):
    # Monitor the SERVER resources
    is_healthy, _ = check_system_resources()
    if not is_healthy:
        return "Pasensya na, the server is a bit busy. Give Guro a second!"

    chain = prompt_template | llm
    # We use 'history' to pass the list of previous messages
    return await chain.ainvoke({
        "question": user_input, 
        "history": chat_history
    })

async def get_guro_response_stream(user_input: str, chat_history: list):
    # Keep your hardware safety check
    is_healthy, _ = check_system_resources()
    if not is_healthy:
        yield "Pasensya na, the server is busy. Give Guro a second!"
        return

    chain = prompt_template | llm
    
    # Use astream to send chunks of text as they are ready
    async for chunk in chain.astream({
        "question": user_input, 
        "history": chat_history
    }):
        yield chunk