from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import json

# Ollama API configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "Mistral-7B-Instruct-v0.3"

# System prompt you want the model to always use
SYSTEM_PROMPT = """
You are an expert assistant. Always provide detailed, clear, and accurate answers. 
Use step-by-step reasoning where appropriate. Maintain a helpful, professional, and concise tone.
"""

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Ollama streaming server is running"}

async def stream_response(user_prompt: str):
    """
    Streams responses from Ollama model using the generate endpoint.
    Combines system prompt with user prompt.
    """
    # Build the combined prompt
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_prompt}\nAssistant:"

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": True
        }) as response:
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    # Depending on Ollama API, the streamed token might be under 'token'
                    token = data.get("token") or data.get("output") or ""
                    if token:
                        yield token
                except json.JSONDecodeError:
                    continue

@app.post("/chat")
async def chat(request: Request):
    """
    Endpoint to chat with the model using streaming.
    """
    data = await request.json()
    user_prompt = data.get("prompt", "")
    if not user_prompt:
        return JSONResponse({"error": "No prompt provided"}, status_code=400)

    return StreamingResponse(stream_response(user_prompt), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)