import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .agent import Agent
from .rag import ingest_text, list_docs

load_dotenv()

app = FastAPI(title="AI Capstone API")
app.mount("/", StaticFiles(directory="web", html=True), name="web")
agent = Agent()

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.get("/docs")
async def docs_list():
    return list_docs()

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not file.filename.endswith((".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only .txt or .md files supported")
    content = (await file.read()).decode("utf-8", errors="ignore")
    count = await ingest_text(file.filename, content)
    return {"chunks": count, "doc_id": file.filename}

@app.post("/query")
async def query(body: dict):
    msg = body.get("message", "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Missing 'message'")
    answer = await agent.chat(msg)
    return {"answer": answer}
