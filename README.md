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

## In PostMan in order to make the output more readable (only for ask) go to Test Results > Generate Tests > Scipts(upper tabs) > Post-response, paste:
    var template = `
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 30px; line-height: 1.8; max-width: 900px; color: #333; background: #f9f9f9; border-radius: 10px;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{{metadata.assistant}} Response</h1>
            <p><strong>Status:</strong> <span style="color: green;">{{status}}</span> | <strong>Model:</strong> {{metadata.model}}</p>
            <hr>
            <div style="white-space: pre-wrap; background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">{{content.answer}}</div>
        </div>
    `;

    // This line sends the JSON data from your backend to the HTML template above
    pm.visualizer.set(template, pm.response.json());

## In PostMan in order to make the output more readable (only for ask/stream) go to Test Results > Generate Tests > Scipts(upper tabs) > Post-response, paste:
        var template = `
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 30px; line-height: 1.8; max-width: 900px; color: #333; background: #f9f9f9; border-radius: 10px;">
        <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Guro Streaming Feed</h1>
        <p><small style="color: #666;">Note: Streaming raw text from Local Server</small></p>
        <hr>
        <div style="white-space: pre-wrap; background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px; font-size: 1.1rem;">
            {{response}}
        </div>
    </div>
`;

// Since it's a stream, we just pass the raw text
pm.visualizer.set(template, { response: pm.response.text() });