from fastapi import FastAPI

app = FastAPI(
    title="Devices Other Service",
    description="Второй сервис для демонстрации API Gateway",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "service": "devices-other-service",
        "message": "Other service for devices",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "devices-other-service",
        "timestamp": "2026-02-27"
    }

@app.get("/api/other")
async def get_other():
    return {
        "service": "other",
        "resource": "other",
        "data": [
            {"id": 1, "name": "other item 1"},
            {"id": 2, "name": "other item 2"},
            {"id": 3, "name": "other item 3"}
        ]
    }

@app.get("/api/other/{item_id}")
async def get_other_item(item_id: int):
    return {
        "service": "other",
        "id": item_id,
        "name": f"other item {item_id}",
        "description": "This is from the other service"
    }

@app.get("/api/other/health")
async def other_health():
    return {"status": "healthy", "service": "other-service"}