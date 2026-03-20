# В этом файле вам необходимо использовать multi-stage и заменить порт и путь к приложению по своему варианту
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY ./app ./app

EXPOSE 8109
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8109"]
