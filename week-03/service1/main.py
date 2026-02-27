from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(
    title="Devices Service",
    description="Сервис для управления устройствами",
    version="1.0.0"
)

# Модель данных для device
class Device(BaseModel):
    id: Optional[int] = None
    name: str
    serial: str  # extra_field из варианта
    type: str
    status: str = "active"

# База данных в памяти
devices_db = []
id_counter = 1

@app.get("/")
async def root():
    return {
        "service": "devices-service",
        "resource": "devices",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "devices-service"}

@app.get("/api/devices")
async def get_devices():
    return devices_db

@app.get("/api/devices/{device_id}")
async def get_device(device_id: int):
    device = next((d for d in devices_db if d["id"] == device_id), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.post("/api/devices")
async def create_device(device: Device):
    global id_counter
    new_device = device.dict()
    new_device["id"] = id_counter
    devices_db.append(new_device)
    id_counter += 1
    return new_device

@app.put("/api/devices/{device_id}")
async def update_device(device_id: int, device: Device):
    for i, d in enumerate(devices_db):
        if d["id"] == device_id:
            updated = device.dict()
            updated["id"] = device_id
            devices_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Device not found")

@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: int):
    for i, d in enumerate(devices_db):
        if d["id"] == device_id:
            devices_db.pop(i)
            return {"message": "Device deleted"}
    raise HTTPException(status_code=404, detail="Device not found")