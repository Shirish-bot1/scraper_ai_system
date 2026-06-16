from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database.db import Base, engine
from app.services.data_fetcher import get_complete_municipality_data, get_full_database_dump
from app.ai_agent import chat_with_agent

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Municipality AI API")

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Municipality AI API is running."}

@app.get("/ask-ai/")
async def query_municipality_info(name: str = Query(...)):
    data = get_complete_municipality_data(name)
    if not data:
        raise HTTPException(status_code=404, detail="Municipality not found")
    return data

class ChatRequest(BaseModel):
    municipality: str
    question: str

@app.post("/chat/")
async def chat_with_ai(request: ChatRequest):
    try:
        answer = chat_with_agent(request.question, request.municipality)
        return {"municipality": request.municipality, "answer": answer}
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}") # This will show the real error in your terminal
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/full-dump")
async def get_all_data():
    return get_full_database_dump()