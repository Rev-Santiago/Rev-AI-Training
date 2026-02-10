# Guro AI Training Backend 

This repository serves as a modular training project for the **GURO Backend**, focusing on the integration of local LLMs with **FastAPI**. It demonstrates core competencies in asynchronous Python, AI orchestration with **LangChain**, and clean architectural patterns optimized for offline TV-based learning systems.

## 🚀 Tech Stack
- **Framework:** FastAPI (Asynchronous)
- **AI Orchestration:** LangGraph & LangChain v0.3
- **Local LLM:** Ollama (Gemma 3:4b)
- **Resource Monitoring:** psutil
- **Environment:** Virtual Environments (venv)
- **Deployment:** Docker & Docker Compose

## 🏗️ Project Structure
The project follows a modular pattern to ensure scalability:
- `app/main.py`: Application entry point and global error handling.
- `app/core/ai_engine.py`: Stateful AI engine, LangGraph definition, and persona logic.
- `app/api/routers/persona.py`: CRUD operations for teacher personas.

- `app/api/routers/query.py`: Main endpoints for standard and LangGraph-based chat.

- `app/api/routers/rag.py`: Handling document uploads and FAISS index ingestion.

app/core/rag_engine.py: Vector store management and embedding generation.

app/core/database.py: Factory Pattern implementation for seamless switching between SQLite and production databases.

## 🌟 Key Features
* **Stateful LangGraph Orchestration**: Uses a directed graph to manage conversation state via `GuroState`, allowing for modular, multi-actor AI workflows.
* **Dynamic Persona CRUD**: Grade-level teaching styles are managed through API endpoints, allowing you to Create, Read, Update, or Delete personas without restarting the server.
* **Streaming Responses**: Real-time "word-by-word" output using `StreamingResponse` to eliminate perceived latency.
* **Resource Guard**: Built-in monitoring via `psutil` to prevent server crashes during high RAM usage.
* **Stateful LangGraph Orchestration**: Manages conversation state via `GuroState`, allowing for modular, multi-actor AI workflows.
* **Retrieval-Augmented Generation (RAG)**: Integrates a `retrieve_context_node` to ground AI responses in local PDF/TXT data.
* **Database Persistence**: Uses SQLAlchemy to store chat history and personas, ensuring data survives server restarts.
* **Factory Pattern Implementation**: Allows the app to switch between SQLite and higher-level databases without changing business logic.
* **Resource Guard**: Built-in monitoring via `psutil` to prevent server crashes during high RAM usage.

## 📖 API Documentation & Usage

### 1. RAG Ingestion (PDF/TXT)
Upload a document to the vector store to provide the AI with new context.
- **Endpoint:** `POST /rag/ingest`
- **Body:** `form-data` with key `file`

### 2. Persistent Graph Query
Query the AI using a specific session ID to maintain history.
- **Endpoint:** `GET /ask/graph`
- **Params:** `query`, `session_id`, `grade`

## 📊 Architecture Flow
```mermaid
graph TD
    User[User] -->|POST /rag/ingest| API_Ingest{RAG API}
    User -->|GET /ask/graph| API_Query{Query API}
    
    subgraph "Guro AI Container"
        direction TB
        API_Ingest -->|Chunk & Embed| Embed[Ollama: nomic-embed-text]
        Embed -->|Save Vectors| FAISS[(FAISS Vector Store)]
        
        API_Query -->|Init State| Graph[LangGraph Workflow]
        
        subgraph "LangGraph Nodes"
            Graph --> Node_Ret[retrieve_context]
            Node_Ret -->|Search| FAISS
            FAISS -->|Return Context| Node_Ret
            
            Node_Ret --> Node_Gen[call_guro_node]
            Node_Gen -->|Prompt + Context| LLM[Ollama: gemma2]
        end
        
        Node_Gen -->|Save History| DB[(SQLite Factory)]
    end
    
    LLM -->|Final Response| User
```

---

## 🛠️ Setup Instructions

### 1. Model Setup
Ensure Ollama is installed and the model is pulled:
bash
```Bash
ollama pull gemma3:4b
```

## Environment Configuration
- **Create a .env file in the root directory:**
Code Snippet
```Bash
MODEL_NAME=gemma3:4b
OLLAMA_BASE_URL=http://localhost:11434
```

## Install Dependencies
Bash
```Bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Server
Bash
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

Bash
```Bash
curl.exe -N "[http://127.0.0.1:8000/ask/stream?query=Explain+Philippine+history+to+a+kid](http://127.0.0.1:8000/ask/stream?query=Explain+Philippine+history+to+a+kid)"
```

---

## Postman Visualization
- To make the output readable in Postman, go to Scripts > Post-response and paste the relevant template:


- **For /ask/graph (Text Stream):**
JavaScript
```JavaScript
    var jsonData = pm.response.json();
    var template = `
        <div style="font-family: 'Segoe UI'; padding: 20px; background: #fdfdfd; border-radius: 10px; border: 1px solid #e0e0e0;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">🍎 Guro Response ({{engine}})</h2>
            <p style="font-style: italic; color: #5dade2;">Context: {{gradeDisplay}} active.</p>
            <div style="white-space: pre-wrap; background: white; padding: 15px; border: 1px solid #eee;">{{content}}</div>
        </div>
    `;

    var rawGrade = decodeURIComponent(pm.request.url.query.get("grade") || "Grade 4");
    pm.visualizer.set(template, {
        engine: jsonData.engine || "LangGraph Direct",
        content: jsonData.answer || jsonData.content.answer,
        gradeDisplay: rawGrade
    });
```

---

## 🐳 Docker Deployment (Windows/WSL 2)
- **The backend is fully containerized to ensure a consistent environment across local servers.**

- 1. Build the Image
- Navigate to the root directory and run:

Bash
```Bash
docker build -t guro-backend:v1 .
```

## 2. Configure Local LLM Access
- **Because the AI engine runs inside a container, it needs a "bridge" to reach the Ollama service on your Windows host.**

- Update .env: Set OLLAMA_BASE_URL to use the Docker internal gateway:

Code snippet
```Bash
OLLAMA_BASE_URL=http://host.docker.internal:11434
```
- **Enable Network Access: You must tell Ollama to accept external calls. In a fresh PowerShell window, run:**

PowerShell
```PowerShell
$env:OLLAMA_HOST="0.0.0.0"
ollama serve
```

## 3. Run the Container
- **Run the Container Simply run the following command to build and start the backend:**

Bash
```Bash
docker-compose up -d --build
```

## 4. Lastly for an example run with a prompt ready
Powershell
```Powershell
curl.exe -N "http://localhost:8000/ask/stream?query=Learn+about+software+development+agile&grade=Grade+7" 
                                                
```

## To restart the image for a cleanly install docker image and it's dependencies
```BASH
docker-compose down
docker-compose up -d --build
```

---

## 🔍 Troubleshooting Docker on Windows
- Connection Errors: If you get a ConnectError, ensure the OLLAMA_HOST environment variable is set to 0.0.0.0 on your Windows machine, not just inside the container.

## For the remaining personas, you can send the following data to your POST /personas/ endpoint:

- TVET: Professional yet easy to understand for career shifter, or beginner, assuming technical skill based vocational education.

- Grade 1: Persona for 6-year-olds: Use very simple words, many emojis, and short sentences. Analogies: Toys and snacks.

- Grade 2: Persona for 7-year-olds: Simple words but introduce basic 'How' and 'Why'. Analogies: Animals and nature.

- Grade 3: Persona for 8-year-olds: Conversational Taglish. Focus on storytelling and curiosity. Analogies: Superheroes and games.

- Grade 4: Persona for 9-year-olds: Balanced English-Tagalog. Use analogies about school and sports.

- Grade 5: Persona for 10-year-olds: Introduce more structured facts and 'Science/History' terms. Analogies: Hobbies and inventions.

- Grade 6: Persona for 11-year-olds: Prepare them for high school. Use critical thinking questions. Analogies: Technology and teamwork.

- Grade 7: Mentor vibe. Use detailed facts, proper terminology, and social analogies.

# How to add them back:
Send a POST request to http://localhost:8000/personas/ for each grade with a JSON body like this:

JSON
```JSON
{
  "grade_level": "Grade 1",
  "description": "Persona for 6-year-olds: Use very simple words, many emojis, and short sentences. Analogies: Toys and snacks."
}
```
Once added, your get_persona_from_db function in the AI engine will immediately begin using these descriptions for new queries.
- Trailing Spaces: Ensure there are no trailing spaces in your .env file values, as these will cause URL parsing failures in the httpx client.

- Low VRAM Mode: On machines with <8GB VRAM (like an RTX 4050), the first response may take 5-10 seconds to stream while the model loads into memory.

---

## 🏗️ Database Factory Pattern Documentation

[cite_start]The Guro AI backend utilizes the **Factory Design Pattern** to manage database connections[cite: 1, 4]. [cite_start]This architecture decouples the core application logic from specific database implementations, allowing developers to switch between different database systems (SQLite, PostgreSQL, MySQL) purely through environment variables without changing a single line of code[cite: 4, 5].

### 🛠️ How it Works
The centralized factory logic resides in `app/core/database.py`. [cite_start]It evaluates the `DB_TYPE` environment variable at runtime to return the appropriate SQLAlchemy engine[cite: 4].

- [cite_start]**Abstraction**: API routes and AI nodes only interact with `SessionLocal`[cite: 4, 15].
- [cite_start]**Portability**: Transition seamlessly from local development (SQLite) to production-grade environments (Postgres/MySQL)[cite: 5, 15].

---

### 🚀 Switching Database Dialects
To change the database system, update your `.env` file with the corresponding configuration.

| Target Database | `DB_TYPE` | `DATABASE_URL` Format | Driver Required |
| :--- | :--- | :--- | :--- |
| **SQLite (Default)** | `sqlite` | Not required (uses internal path) | Built-in |
| **PostgreSQL** | `postgresql` | `postgresql://user:pass@host:port/dbname` | `psycopg2-binary` |
| **MySQL** | `mysql` | `mysql+pymysql://user:pass@host:port/dbname` | `pymysql` |

---

### 📖 Step-by-Step Configuration

#### 1. Using SQLite (Local Development)
Ideal for testing and OJT activities where a local file is preferred.
- **Environment**: Set `DB_TYPE=sqlite` (or leave it blank).
- [cite_start]**Persistence**: Data is saved to `/app/data/guro.db`.

#### 2. Using PostgreSQL (Production)
1. Ensure your PostgreSQL server is running.
2. Update your `.env`:
   ```bash
   DB_TYPE=postgresql
   DATABASE_URL=postgresql://admin:secret@localhost:5432/guro_prod

#### 3. Using MqSQL
1. Ensure pymysql is included in your requirements.txt.
2. Update your .env:
    ```bash
    DB_TYPE=mysql
    DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/guro_db

---

### 🔍 Technical Implementation
The factory employs defensive coding to provide fallbacks and ensure type safety for the SQLAlchemy engine:
```Python
        def get_engine():
            # Detect dialect from environment
            if DB_TYPE == "postgresql":
                url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname")
                return create_engine(url)
            
            elif DB_TYPE == "mysql":
                url = os.getenv("DATABASE_URL", "mysql+pymysql://user:pass@localhost:3306/dbname")
                return create_engine(url)
            
            # Default Fallback: Persistent SQLite
            return create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
```

### 🐳 Docker Persistence
When utilizing the Factory Pattern within Docker, ensure your docker-compose.yml mounts the ./data volume to persist SQLite files or local configuration.

    ```YAML
    volumes:
    - ./data:/app/data