import asyncio
import websockets
import json
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Хранилище подключений
CONNECTIONS = set()
# Храним последние сообщения для новых клиентов
last_offer = None
last_candidates = []

async def handler(websocket):
    # Обработчик WebSocket соединений. Пересылает сообщения между клиентами
    global last_offer, last_candidates
    
    # Генерируем ID для клиента
    client_id = id(websocket)
    CONNECTIONS.add(websocket)
    
    logger.info(f"Клиент {client_id} подключился. Всего клиентов: {len(CONNECTIONS)}")
    
    # Если есть сохраненный offer, отправляем его новому клиенту
    if last_offer and len(CONNECTIONS) > 1:
        logger.info(f"Отправка сохраненного offer новому клиенту {client_id}")
        await websocket.send(json.dumps(last_offer))
    
    # Отправляем сохраненные кандидаты
    for candidate in last_candidates:
        logger.info(f"Отправка сохраненного candidate клиенту {client_id}")
        await websocket.send(json.dumps(candidate))
    
    try:
        async for message in websocket:
            try:
                # Пробуем распарсить как JSON
                data = json.loads(message)
                msg_type = data.get('type', 'unknown')
                logger.info(f"Получено сообщение типа '{msg_type}' от {client_id}")
                
                # Сохраняем offer и кандидаты
                if msg_type == 'offer':
                    last_offer = data
                    logger.info("Offer сохранен")
                elif msg_type == 'candidate':
                    last_candidates.append(data)
                    logger.info(f"Candidate сохранен (всего: {len(last_candidates)})")
                
            except Exception as e:
                logger.error(f"Ошибка парсинга: {e}")
                continue
            
            # Рассылаем сообщение всем остальным подключенным клиентам
            recipients = 0
            for conn in CONNECTIONS:
                if conn != websocket:
                    try:
                        await conn.send(message)
                        recipients += 1
                    except Exception as e:
                        logger.error(f"Ошибка отправки клиенту: {e}")
            
            logger.info(f"Сообщение переслано {recipients} клиентам")
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Клиент {client_id} отключился (нормально)")
    except Exception as e:
        logger.error(f"Ошибка в обработчике: {e}")
    finally:
        CONNECTIONS.remove(websocket)
        logger.info(f"Клиент {client_id} отключен. Осталось: {len(CONNECTIONS)}")
        
        # Если не осталось клиентов, очищаем сохраненные данные
        if len(CONNECTIONS) == 0:
            last_offer = None
            last_candidates = []
            logger.info("Очередь очищена (нет клиентов)")


async def main():
    # Запуск Signaling сервера
    host = "localhost"
    port = 8765
    
    logger.info("~" * 60)
    logger.info("WebRTC SIGNALING SERVER")
    logger.info("~" * 60)
    logger.info(f"Project code: logs-s03")
    logger.info(f"Сервер запускается на {host}:{port}")
    logger.info("Ожидание подключений...")
    logger.info("~" * 60)
    
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # работаем вечно

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nСервер остановлен")