import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"

async def generate(prompt: str):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        })
        response.raise_for_status()
        return response.json()["response"]