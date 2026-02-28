import strawberry
from typing import List, Optional
from .database import get_all_devices, get_device_by_id, create_device_in_db

# Резолверы для полей Device
def get_device_status(root) -> str:
    return root.get("status", "active")

def get_device_created_at(root) -> str:
    return root.get("createdAt", "2026-02-28")

# Резолверы для Query
def get_devices() -> List[dict]:
    """Возвращает список всех устройств"""
    return get_all_devices()

def get_device(root, id: strawberry.ID) -> Optional[dict]:
    """Возвращает устройство по ID"""
    try:
        device_id = int(id)
        return get_device_by_id(device_id)
    except ValueError:
        return None

# Резолверы для Mutation
def create_device(name: str, serial: str, status: Optional[str] = "active") -> dict:
    """Создает новое устройство"""
    device_data = {
        "name": name,
        "serial": serial,
        "status": status,
        "createdAt": "2026-02-28"
    }
    return create_device_in_db(device_data)