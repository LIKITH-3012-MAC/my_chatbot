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
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": False
    }
    
    try:
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return {"response": data.get("response", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))