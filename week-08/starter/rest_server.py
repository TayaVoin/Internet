from fastapi import FastAPI, HTTPException
import uvicorn
import time
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Bookings REST API")

# База данных
bookings_db = {}
booking_counter = 0

class BookingCreate(BaseModel):
    user_id: str
    item_id: str
    date: str

class Booking(BookingCreate):
    id: str
    status: str
    created_at: int
    updated_at: int

@app.post("/bookings", response_model=Booking)
async def create_booking(booking: BookingCreate):
    global booking_counter
    booking_counter += 1
    booking_id = f"booking_{booking_counter}"
    
    new_booking = Booking(
        id=booking_id,
        user_id=booking.user_id,
        item_id=booking.item_id,
        date=booking.date,
        status="confirmed",
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    
    bookings_db[booking_id] = new_booking.dict()
    return new_booking

@app.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    if booking_id in bookings_db:
        return bookings_db[booking_id]
    raise HTTPException(status_code=404, detail="Booking not found")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)