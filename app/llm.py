import os, httpx
from typing import List, Dict

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

class LLM:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.base_url}/api/chat"
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json={"model": self.model, "messages": messages, "stream": False})
            r.raise_for_status()
            data = r.json()
            return data.get("message", {}).get("content", "")

async def embed_texts(texts: List[str]) -> List[List[float]]:
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    vecs = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for t in texts:
            r = await client.post(url, json={"model": OLLAMA_EMBED_MODEL, "prompt": t})
            r.raise_for_status()
            vecs.append(r.json().get("embedding"))
    return vecs
