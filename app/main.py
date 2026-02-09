from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager # 1. Import this
from app.api.routes import router 
from app.core.database import init_db

# 2. Define the lifespan logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run before the app starts
    init_db() 
    yield
    # Shutdown: Run when the app stops (optional cleanup)
    pass

# 3. Pass the lifespan to the FastAPI instance
app = FastAPI(title="GURO AI Training", lifespan=lifespan)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "AI Training Server Online", "user": "Rev"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Guro encountered an error", "details": str(exc)},
    )