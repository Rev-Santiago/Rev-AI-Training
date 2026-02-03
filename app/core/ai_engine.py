from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from app.core.config import MODEL_NAME # This is your basic import!

# Now we use the variable from .env
llm = Ollama(model=MODEL_NAME)

async def get_guro_response(user_input: str):
    template = "You are a helpful teaching assistant named Guro. Answer this in taglish, make sure that the information is easily digested by a grade 7 student in the Philippines: {question}"
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    # .ainvoke is the asynchronous version of invoke
    return await chain.ainvoke({"question": user_input})