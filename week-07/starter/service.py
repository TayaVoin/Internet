import grpc
import sys
import time
from concurrent import futures
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'generated'))

import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

notifications_db = {}
notification_counter = 0

class NotificationsService(pb2_grpc.NotificationsServiceServicer):
    # Реализация gRPC сервиса для уведомлений
    def SendNotification(self, request, context):

        # Обрабатывает запрос на отправку уведомления
        global notification_counter
        
        # Генерируем ID если не указан
        notification_id = request.id
        if not notification_id:
            notification_counter += 1
            notification_id = f"notif_{notification_counter}"
        
        # Сохраняем уведомление в "базу данных"
        notifications_db[notification_id] = {
            "id": notification_id,
            "recipient": request.recipient,
            "message": request.message,
            "channel": request.channel,
            "created_at": request.created_at or int(time.time()),
            "status": "queued"
        }
        
        print(f"Получено уведомление для {request.recipient} через {request.channel}")
        print(f"Сообщение: {request.message}")
        
        success = True
        status = "sent"
        
        if not request.channel or not request.message:
            success = False
            status = "failed"
        
        notifications_db[notification_id]["status"] = status
        
        # Формируем ответ
        return pb2.SendNotificationResponse(
            id=notification_id,
            success=success,
            status=status,
            message="Уведомление отправлено" if success else "Ошибка отправки"
        )
    
    def GetNotificationStatus(self, request, context):
        # Возвращает статус уведомления по ID
        notification_id = request.id
        
        if notification_id in notifications_db:
            notif = notifications_db[notification_id]
            return pb2.NotificationStatusResponse(
                id=notif["id"],
                status=notif["status"],
                channel=notif["channel"],
                sent_at=notif.get("created_at", 0),
                delivered_at=notif.get("delivered_at", 0)
            )
        else:
            # Уведомление не найдено
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Уведомление с ID {notification_id} не найдено")
            return pb2.NotificationStatusResponse()

def serve():
    # Запускает gRPC сервер
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    pb2_grpc.add_NotificationsServiceServicer_to_server(NotificationsService(), server)
    
    port = '50051'
    server.add_insecure_port(f'[::]:{port}')
    
    print(f"gRPC сервер запущен на порту {port}")
    print(f"Сервис: NotificationsService")
    print(f"Пакет: notifications.v1")
    print(f"Project code: notifications-s03")
    print("~" * 50)
    print("Доступные методы:")
    print("  • SendNotification(request) -> SendNotificationResponse")
    print("  • GetNotificationStatus(request) -> NotificationStatusResponse")
    print("~" * 50)
    print("Press Ctrl+C to stop")
    
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nСервер остановлен")

if __name__ == '__main__':
    serve()