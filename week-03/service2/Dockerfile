FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Порт для второго сервиса (не конфликтует с первым)
EXPOSE 8107

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8107"]