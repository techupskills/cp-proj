[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/techupskills/cp-proj?quickstart=1)
> Replace `REPO_OWNER/REPO_NAME` with your repository path once you push this project to GitHub.

# AI Capstone Project

Demonstrates: RAG over local docs, an agent that can call tools (via MCP), and a minimal web UI.
Defaults to a local Ollama model (llama3.2).

## Architecture (Mermaid)
```mermaid
flowchart LR
    U[User] --> UI[Web UI]
    UI --> API[FastAPI Backend]
    API --> AG[Agent]
    AG -->|Prompt+Context| LLM[Ollama Model]
    AG -->|Retrieve| VS[Vector Store (Chroma)]
    VS --> DOCS[Local Docs]
    AG -->|Tools via MCP| MCP[MCP Client]
    MCP --> SRV[FastMCP Server]
    SRV --> TOOLS[Tools/Resources]
    LLM --> AG
    AG --> API
    API --> UI
```

## Quick Start (local)
ollama pull llama3.2
ollama pull nomic-embed-text
cp .env.example .env
pip install -r requirements.txt
python mcp_server/server.py   # optional tools
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
Open http://localhost:8080

## Running in GitHub Codespaces
1. Push this repo to GitHub and click **Code → Create codespace on main**.
2. The devcontainer will install Ollama and Python deps, then auto-start:
   - **8080** → API + Web UI (chat)
   - **8000** → MCP endpoint (/mcp)
3. Manual restart:
   - `bash .devcontainer/bootstrap.sh`
   - Or VS Code **Tasks**: “Start: MCP server”, “Start: API”

Logs: `/workspaces/logs/`

## Endpoints
POST /ingest  (upload .txt/.md)
GET  /docs
POST /query   {"message":"..."}
GET  /health
