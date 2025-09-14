import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from .llm import embed_texts

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
client = chromadb.PersistentClient(path=DB_DIR, settings=Settings(allow_reset=True))
collection = client.get_or_create_collection(name="docs")

def _chunk(text: str, max_len: int = 600, overlap: int = 120) -> List[str]:
    words = text.split()
    res, buf, count = [], [], 0
    for w in words:
        buf.append(w); count += len(w) + 1
        if count >= max_len:
            res.append(" ".join(buf))
            buf = buf[-overlap:] if overlap > 0 else []
            count = sum(len(x)+1 for x in buf)
    if buf: res.append(" ".join(buf))
    return res

async def ingest_text(doc_id: str, text: str) -> int:
    chunks = _chunk(text)
    embeds = await embed_texts(chunks)
    ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
    metas = [{"doc_id": doc_id, "chunk": i} for i in range(len(chunks))]
    collection.upsert(ids=ids, documents=chunks, embeddings=embeds, metadatas=metas)
    return len(chunks)

async def retrieve(query: str, n: int = 4) -> List[Dict]:
    qvec = (await embed_texts([query]))[0]
    results = collection.query(query_embeddings=[qvec], n_results=n)
    items = []
    for doc, meta in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0]):
        items.append({"text": doc, "doc_id": meta.get("doc_id"), "chunk": meta.get("chunk")})
    return items

def list_docs() -> List[str]:
    try:
        metas = collection.get(include=["metadatas"])
        seen = []
        for m in metas.get("metadatas", []):
            for mm in m:
                did = mm.get("doc_id")
                if did and did not in seen:
                    seen.append(did)
        return seen
    except Exception:
        return []
