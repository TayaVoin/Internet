from fastapi import FastAPI

app = FastAPI(title="Reviews Service", version="1.0.0")

@app.get("/")
async def root():
    return {"service": "reviews", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "port": 8109}