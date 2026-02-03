from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routes import router # Importing your route file

app = FastAPI(title="GURO AI Training")

# Include the routes we just made
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