# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     OLLAMA_BASE_URL=http://host.docker.internal:11434     OLLAMA_MODEL=llama3.2     OLLAMA_EMBED_MODEL=nomic-embed-text     MCP_SERVER_URL=http://host.docker.internal:8000/mcp     API_HOST=0.0.0.0     API_PORT=8080

RUN apt-get update -y && apt-get install -y --no-install-recommends \ 
    build-essential curl git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
