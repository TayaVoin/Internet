from fastapi import FastAPI
import os
import socket

app = FastAPI(title="Messages Service", version="1.0.0")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

@app.get("/")
async def root():
    return {
        "service": "messages-svc-s03",
        "status": "running",
        "hostname": socket.gethostname()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "db_host": DB_HOST,
        "db_port": DB_PORT
    }

@app.get("/api/messages")
async def get_messages():
    return {"messages": []}

@app.get("/api/messages/{message_id}")
async def get_message(message_id: int):
    return {"id": message_id, "text": f"Message {message_id}", "topic": "general"}