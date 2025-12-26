from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    model: str = "llama3.2" 

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    ollama_url = "http://localhost:11434/api/generate"
    payload = {"model": request.model, "prompt": request.prompt, "stream": False}
    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        return {"response": response.json().get("response", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz")
async def quiz_endpoint(request: ChatRequest):
    quiz_prompt = (
        f"Generate a professional 3-question MCQ Quiz on: {request.prompt}. "
        "Format: Questions followed by A,B,C,D options. "
        "List the Answer Key clearly at the end."
    )
    payload = {"model": request.model, "prompt": quiz_prompt, "stream": False}
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        return {"quiz": response.json().get("response", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
