# Guro AI Training Backend 🍎

This repository serves as a modular training project for the **GURO Backend**, focusing on the integration of local LLMs with **FastAPI**. It demonstrates core competencies in asynchronous Python, AI orchestration with **LangChain**, and clean architectural patterns optimized for offline TV-based learning systems.

## 🚀 Tech Stack
- **Framework:** FastAPI (Asynchronous)
- **AI Orchestration:** LangChain v0.3
- **Local LLM:** Ollama (Gemma 3:4b)
- **Resource Monitoring:** psutil
- **Environment:** Virtual Environments (venv)

## 🏗️ Project Structure
The project follows a modular pattern to ensure scalability:
- `app/main.py`: Application entry point and global error handling.
- `app/api/`: Contains API route definitions and streaming logic.
- `app/core/`: Houses the AI engine, memory management, and environment configuration.

## 🌟 Key Features
* **Streaming Responses**: Real-time "word-by-word" output using `StreamingResponse` to eliminate perceived latency.
* **Decoupled Architecture**: Optimized for a Local Server + TV Client setup, offloading heavy AI inference from weak TV hardware.
* **Resource Guard**: Built-in monitoring to prevent server crashes during high RAM usage.
* **Sliding Window Memory**: Context-aware teaching that remembers the last 3 conversation turns without bloating memory.



## 🛠️ Setup Instructions

### 1. Model Setup
Ensure Ollama is installed and the model is pulled:
```bash
ollama pull gemma3:4b
```

## Environment Configuration
- **Create a .env file in the root directory:**
```Code Snippet
MODEL_NAME=gemma3:4b
OLLAMA_BASE_URL=http://localhost:11434
```

## Install Dependencies
```Bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Server
```Bash
uvicorn app.main:app --reload
```

## 📖 API Documentation & Usage
- **Standard Request (GET)**
```
http://127.0.0.1:8000/ask?query={query}
```

- **Streaming Request (Real-time)**
- To see the text generation in real-time within your terminal:

```Bash
curl.exe -N "[http://127.0.0.1:8000/ask/stream?query=Explain+Philippine+history+to+a+kid](http://127.0.0.1:8000/ask/stream?query=Explain+Philippine+history+to+a+kid)"
```

## Postman Visualization
- To make the output readable in Postman, go to Scripts > Post-response and paste the relevant template:

- **For /ask (JSON):**
```JavaScript
    var template = `
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 30px; line-height: 1.8; max-width: 900px; color: #333; background: #f9f9f9; border-radius: 10px;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{{metadata.assistant}} Response</h1>
            <p><strong>Status:</strong> <span style="color: green;">{{status}}</span> | <strong>Model:</strong> {{metadata.model}}</p>
            <hr>
            <div style="white-space: pre-wrap; background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">{{content.answer}}</div>
        </div>
    `;
    pm.visualizer.set(template, pm.response.json());
```
- **For /ask/stream (Text Stream):**
```JavaScript
    var template = `
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 30px; line-height: 1.8; max-width: 900px; color: #333; background: #f9f9f9; border-radius: 10px;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Guro Streaming Feed</h1>
            <hr>
            <div style="white-space: pre-wrap; background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px; font-size: 1.1rem;">
                {{response}}
            </div>
        </div>
    `;
    pm.visualizer.set(template, { response: pm.response.text() });
```

## 🐳 Docker Deployment (Windows/WSL 2)
- **The backend is fully containerized to ensure a consistent environment across local servers.**

- 1. Build the Image
- Navigate to the root directory and run:
```
Bash
docker build -t guro-backend:v1 .
```

## 2. Configure Local LLM Access
- **Because the AI engine runs inside a container, it needs a "bridge" to reach the Ollama service on your Windows host.**

- Update .env: Set OLLAMA_BASE_URL to use the Docker internal gateway:
```
Code snippet
OLLAMA_BASE_URL=http://host.docker.internal:11434
```
- **Enable Network Access: You must tell Ollama to accept external calls. In a fresh PowerShell window, run:**

```
PowerShell
$env:OLLAMA_HOST="0.0.0.0"
ollama serve
```

## 3. Run the Container
- **Use the --add-host flag to map the host gateway and --env-file to pass your configuration:**
```
Bash
docker run -d -p 8000:8000 --env-file .env --add-host=host.docker.internal:host-gateway --name guro-app guro-backend:v1
```
## 🔍 Troubleshooting Docker on Windows
- Connection Errors: If you get a ConnectError, ensure the OLLAMA_HOST environment variable is set to 0.0.0.0 on your Windows machine, not just inside the container.

- Trailing Spaces: Ensure there are no trailing spaces in your .env file values, as these will cause URL parsing failures in the httpx client.

- Low VRAM Mode: On machines with <8GB VRAM (like an RTX 4050), the first response may take 5-10 seconds to stream while the model loads into memory.