# Guro AI Training Backend

This repository serves as a modular training project for the **GURO Backend**, focusing on the integration of local LLMs with FastAPI. It demonstrates core competencies in asynchronous Python, AI orchestration with LangChain, and clean architectural patterns.

## 🚀 Tech Stack
- **Framework:** FastAPI (Asynchronous)
- **AI Orchestration:** LangChain v0.3
- **Local LLM:** Ollama (Gemma 3:4b)
- **Configuration:** Python-Dotenv
- **Environment:** Virtual Environments (venv)

## 🏗️ Project Structure
The project follows a modular pattern to ensure scalability:
- `app/main.py`: Application entry point and global error handling.
- `app/api/`: Contains API route definitions and data processing logic.
- `app/core/`: Houses the AI engine and environment configuration.

## 🛠️ Setup Instructions
1. **Model Setup:**
   Ensure Ollama is installed and the model is pulled:
   ```bash
   ollama pull gemma3:4b

## Environment configuration used in ver 1.0
    MODEL_NAME=gemma3:4b

## Install dependencies
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt

## How to Run the server
    uvicorn app.main:app --reload

## How to prompt using GET(PostMan)
    http://127.0.0.1:8000/ask?query={query here}?
    ex. http://127.0.0.1:8000/ask?query=What is a list comprehension?

