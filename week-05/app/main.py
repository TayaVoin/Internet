import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional

from .database import clear_db
from .resolvers import (
    get_devices, get_device, create_device,
    get_device_status, get_device_created_at
)

# Определяем GraphQL типы
@strawberry.type
class Device:
    id: strawberry.ID
    name: str
    serial: str
    status: Optional[str] = None
    created_at: Optional[str] = None
    
    # Резолверы для полей
    @strawberry.field
    def status(self) -> str:
        return get_device_status({"status": self.status})
    
    @strawberry.field
    def created_at(self) -> str:
        return get_device_created_at({"createdAt": self.created_at})

# Определяем Query
@strawberry.type
class Query:
    @strawberry.field
    def devices(self) -> List[Device]:
        devices_data = get_devices()
        return [
            Device(
                id=strawberry.ID(str(d["id"])),
                name=d["name"],
                serial=d["serial"],
                status=d.get("status"),
                created_at=d.get("createdAt")
            )
            for d in devices_data
        ]
    
    @strawberry.field
    def device(self, id: strawberry.ID) -> Optional[Device]:
        device_data = get_device(None, id)
        if device_data:
            return Device(
                id=strawberry.ID(str(device_data["id"])),
                name=device_data["name"],
                serial=device_data["serial"],
                status=device_data.get("status"),
                created_at=device_data.get("createdAt")
            )
        return None

# Определяем Mutation
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_device(self, name: str, serial: str, status: Optional[str] = "active") -> Device:
        device_data = create_device(name, serial, status)
        return Device(
            id=strawberry.ID(str(device_data["id"])),
            name=device_data["name"],
            serial=device_data["serial"],
            status=device_data.get("status"),
            created_at=device_data.get("createdAt")
        )

# Создаем схему
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Создаем FastAPI приложение
app = FastAPI(title="Devices GraphQL API", version="1.0.0")

# Добавляем GraphQL роутер
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "devices-graphql"}

# Очистка базы
@app.post("/clear")
async def clear():
    clear_db()
    return {"message": "Database cleared"}

@app.get("/")
async def root():
    return {
        "service": "Devices GraphQL API",
        "endpoint": "/graphql",
        "playground": "/graphql"
    }