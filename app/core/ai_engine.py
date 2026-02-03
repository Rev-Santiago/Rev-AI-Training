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

def get_persona_for_grade(grade: str):
    """Returns a tailored teaching style based on grade level."""
    # Define our curriculum personas
    personas = {
        "Grade 1": "Persona for 6-year-olds: Use very simple words, many emojis, and short sentences. Analogies: Toys and snacks.",
        "Grade 2": "Persona for 7-year-olds: Simple words but introduce basic 'How' and 'Why'. Analogies: Animals and nature.",
        "Grade 3": "Persona for 8-year-olds: Conversational Taglish. Focus on storytelling and curiosity. Analogies: Superheroes and games.",
        "Grade 4": "Persona for 9-year-olds: Balanced English-Tagalog. Use analogies about school and sports.",
        "Grade 5": "Persona for 10-year-olds: Introduce more structured facts and 'Science/History' terms. Analogies: Hobbies and inventions.",
        "Grade 6": "Persona for 11-year-olds: Prepare them for high school. Use critical thinking questions. Analogies: Technology and teamwork.",
        "Grade 7": "Persona for 12-13 year olds: Mentor vibe. Use detailed facts, proper terminology, and social analogies."
    }
    
    # Default to Grade 4 if they send something weird
    return personas.get(grade, personas["Grade 4"])

async def get_guro_response_stream(user_input: str, chat_history: list, grade: str = "Grade 1"):
    # Hardware Safety Check
    is_healthy, _ = check_system_resources()
    if not is_healthy:
        yield "Pasensya na, the server is busy. Give Guro a second!"
        return

    # Select the persona dynamically
    persona_instruction = get_persona_for_grade(grade)
    
    system_prompt = f"You are Guro, a legendary Filipino teacher. {persona_instruction} Always stay friendly and relatable."

    dynamic_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = dynamic_prompt | llm
    async for chunk in chain.astream({"question": user_input, "history": chat_history}):
        yield chunk