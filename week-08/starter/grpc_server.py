import grpc
import sys
import time
import threading
from concurrent import futures
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'generated'))

import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

bookings_db = {}
booking_counter = 0
booking_updates = []


class BookingsService(pb2_grpc.BookingsServiceServicer):
    def CreateBooking(self, request, context):

        global booking_counter
        
        booking_counter += 1
        booking_id = f"booking_{booking_counter}"
        
        booking = {
            "id": booking_id,
            "user_id": request.user_id,
            "item_id": request.item_id,
            "date": request.date,
            "status": "confirmed",
            "created_at": int(time.time()),
            "updated_at": int(time.time())
        }
        
        bookings_db[booking_id] = booking
        
        booking_updates.append({
            "id": booking_id,
            "user_id": request.user_id,
            "status": "confirmed",
            "message": f"Booking {booking_id} created",
            "timestamp": int(time.time())
        })
        
        print(f"Создано бронирование: {booking_id} для пользователя {request.user_id}")
        
        return pb2.Booking(
            id=booking_id,
            user_id=request.user_id,
            item_id=request.item_id,
            date=request.date,
            status="confirmed",
            created_at=booking["created_at"],
            updated_at=booking["updated_at"]
        )
    
    def GetBooking(self, request, context):
        booking_id = request.id
        
        if booking_id in bookings_db:
            b = bookings_db[booking_id]
            return pb2.Booking(
                id=b["id"],
                user_id=b["user_id"],
                item_id=b["item_id"],
                date=b["date"],
                status=b["status"],
                created_at=b["created_at"],
                updated_at=b["updated_at"]
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Бронирование {booking_id} не найдено")
            return pb2.Booking()
    
    def SubscribeBookings(self, request, context):
        user_id = request.user_id
        limit = request.limit if request.limit > 0 else 10
        
        print(f"Клиент {user_id} подписался на обновления (max: {limit})")
        
        user_updates = [u for u in booking_updates if u["user_id"] == user_id]
        
        # Отправляем последние limit обновлений
        for update in user_updates[-limit:]:
            time.sleep(0.1)
            
            yield pb2.BookingUpdate(
                id=update["id"],
                user_id=update["user_id"],
                status=update["status"],
                message=update["message"],
                timestamp=update["timestamp"]
            )
        print(f"Стриминг завершен для {user_id}")

def serve():
    # Запускает gRPC сервер
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_BookingsServiceServicer_to_server(BookingsService(), server)
    
    port = '50051'
    server.add_insecure_port(f'[::]:{port}')
    
    print(f"gRPC сервер запущен на порту {port}")
    print(f"Сервис: BookingsService")
    print(f"Пакет: bookings.v1")
    print(f"Project code: bookings-s03")
    print("~" * 50)
    print("Unary методы:")
    print("  • CreateBooking(request) -> Booking")
    print("  • GetBooking(request) -> Booking")
    print("Server Streaming:")
    print("  • SubscribeBookings(request) -> stream BookingUpdate")
    print("~" * 50)
    print("Press Ctrl+C to stop")
    
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nСервер остановлен")

if __name__ == '__main__':
    serve()