#!/usr/bin/env bash
set -euo pipefail
export $(grep -v '^#' .env 2>/dev/null | xargs) || true
mkdir -p /workspaces/logs

if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
  nohup ollama serve > /workspaces/logs/ollama.log 2>&1 &
  for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then break; fi
    sleep 1
  done
fi

if ! ollama list | awk '{print $1}' | grep -q "^llama3.2$"; then ollama pull llama3.2 || true; fi
if ! ollama list | awk '{print $1}' | grep -q "^nomic-embed-text$"; then ollama pull nomic-embed-text || true; fi

if ! lsof -i:8000 >/dev/null 2>&1; then nohup python mcp_server/server.py > /workspaces/logs/mcp_server.log 2>&1 & fi
AP="${API_PORT:-8080}"
if ! lsof -i:$AP >/dev/null 2>&1; then nohup uvicorn app.main:app --host "${API_HOST:-0.0.0.0}" --port "$AP" --reload > /workspaces/logs/api.log 2>&1 & fi
