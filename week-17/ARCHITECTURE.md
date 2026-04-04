# Архитектура сервиса событий (events-s03)

## Информация о проекте
- **Студент**: Воинова Таисия А.
- **Группа**: 432 | **ID**: s03
- **Проект**: events-s03
- **Ресурс**: events

## Обзор системы
Система предназначена для управления событиями (events) и состоит из трех микросервисов:

1. **Events Service** (основной сервис) — управление событиями (CRUD)
2. **Notification Service** — отправка уведомлений о новых событиях
3. **API Gateway** — единая точка входа для клиентов

## Диаграмма взаимодействия
| Отправитель | Получатель | Протокол | Метод | Описание |
|-------------|------------|----------|-------|----------|
| Клиент | Gateway | REST | `GET /api/events` | Получение списка событий |
| Клиент | Gateway | REST | `POST /api/events` | Создание события |
| Gateway | Events Service | gRPC | `ListEvents` | Запрос списка от основного сервиса |
| Gateway | Events Service | gRPC | `CreateEvent` | Создание события в БД |
| Events Service | Notification Service | gRPC | `SendEventCreated` | Уведомление о новом событии |
| Events Service | PostgreSQL | SQL | `SELECT/INSERT` | Работа с данными |
```
[Клиент]
│
│ REST (8080)
▼
[Gateway Nginx]
│
│ gRPC (внутренняя сеть Docker)
▼
[Events Service:8197] ──gRPC──► [Notification Service]
│
│ SQL (5432)
▼
[PostgreSQL Database]
```

## Технологический стек

| Компонент | Технология | Обоснование |
|-----------|------------|-------------|
| **Events Service** | FastAPI + Python | Высокая производительность, простота разработки |
| **Notification Service** | FastAPI + Python | Единый стек с основным сервисом |
| **API Gateway** | Nginx | Легковесный, быстрый прокси |
| **База данных** | PostgreSQL | Надежность, транзакции, ACID |
| **Межсервисное общение** | gRPC | Высокая скорость, бинарный протокол |
| **Внешнее API** | REST | Удобно для фронтенда и клиентов |
| **Контейнеризация** | Docker + Compose | Локальная разработка |
| **Оркестрация** | Kubernetes (опционально) | Для продакшена |
| **CI/CD** | GitHub Actions | Автоматизация тестов и сборки |

## Протоколы взаимодействия

### Внешнее API (REST)
- `GET /api/events` — список событий
- `POST /api/events` — создание события
- `GET /api/events/{id}` — детали события

### Межсервисное взаимодействие (gRPC)
**Events Service → Notification Service**:
```protobuf
service NotificationService {
  rpc SendEventCreated (EventNotification) returns (NotificationResponse);
}
```

**Gateway → Events Service:**
```protobuf
service EventsService {
  rpc GetEvent (GetEventRequest) returns (Event);
  rpc CreateEvent (CreateEventRequest) returns (Event);
  rpc ListEvents (ListEventsRequest) returns (stream Event);
}
```

## Базы данных

### Events Service (PostgreSQL)
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    date TIMESTAMP,
    created_by INT,
    status VARCHAR(50)
);
```

### Notification Service (SQLite для простоты)
- Хранит историю отправленных уведомлений

## Обработка ошибок и отказоустойчивость
| Стратегия	| Где применяется |	Описание |
| Retry	| gRPC вызовы |	При временных ошибках сети (3 попытки) |
| Timeout |	Все запросы | 5 секунд на ответ, иначе fallback |
| Circuit Breaker | Notification Service | Если сервис падает, отключаем уведомления |
| Graceful degradation | API | Если Notification не работает, события все равно создаются |
| Fallback | Уведомления | Сохраняем в БД и отправляем позже |

## Масштабирование
|Сервис | Стратегия	| Почему |
| Events Service | Горизонтальное (3+ реплик) | Основная нагрузка |
| Notification Service | 2 реплики | Не критичный, может отставать |
| Gateway |	2 реплики |	Точка входа, нужна отказоустойчивость |

## Безопасность
| Уровень |	Мера |
| Транспорт | HTTPS для внешних запросов |
| Аутентификация | JWT токены (в заголовке Authorization) |
| Авторизация | Проверка прав доступа к событиям |
| Межсервисная | mTLS (в проде) или внутренняя сеть Docker |
| Секреты | В переменных окружения, не в коде |

## Деплой и CI/CD

### CI/CD пайплайн (GitHub Actions)
1. Линтер (flake8)
2. Тесты (pytest)
3. Сборка Docker образов
4. Публикация в registry
5. Деплой на staging

### Zero-downtime deployment
- Rolling update в Kubernetes
- Healthchecks для каждого сервиса
- Graceful shutdown (обработка SIGTERM)

## Мониторинг и логирование
| Метрика | Инструмент |
| Логи | stdout + ELK (опционально) |
| Метрики | Prometheus + Grafana |
| Трейсинг | Jaeger (опционально) |
| Healthchecks | /health эндпоинты |

## Локальный запуск

### Требования
- Docker + Docker Compose
- Make (опционально)

### Команды
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Эндпоинты
- API Gateway: http://localhost:8080
- Events Service (прямой): http://localhost:8197
- Swagger UI: http://localhost:8080/docs

## Примеры запросов

### Создание события
```bash
curl -X POST http://localhost:8080/api/events \
  -H "Content-Type: application/json" \
  -d '{"title":"Концерт","location":"Москва","date":"2026-12-31"}'
```

### Получение списка
```bash
curl http://localhost:8080/api/events
```
## Выводы

### Сильные стороны архитектуры
- Независимость сервисов (слабосвязанные)
- Асинхронность через gRPC
- Масштабируемость
- Документированность

### Что можно улучшить
- Добавить очередь сообщений (RabbitMQ/Kafka)
- Внедрить Circuit Breaker паттерн
- Добавить кэширование (Redis)
- Полный переход на Kubernetes