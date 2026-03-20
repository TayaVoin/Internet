import time
import requests
import grpc
import sys
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.path.append(str(Path(__file__).parent.parent / 'generated'))

import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

# Конфигурация
REST_URL = "http://localhost:8000/bookings"
GRPC_ADDR = "localhost:50051"
REQUESTS_COUNT = 1000
WARMUP_COUNT = 100
CONCURRENT_WORKERS = 10

def warmup():
    print(f"Прогрев: {WARMUP_COUNT} запросов...")
    
    # REST прогрев
    for i in range(WARMUP_COUNT):
        try:
            requests.post(REST_URL, json={
                "user_id": f"user_{i}",
                "item_id": f"item_{i}",
                "date": "2026-03-02"
            })
        except:
            pass
    
    # gRPC прогрев
    try:
        with grpc.insecure_channel(GRPC_ADDR) as channel:
            stub = pb2_grpc.BookingsServiceStub(channel)
            for i in range(WARMUP_COUNT):
                stub.CreateBooking(pb2.CreateBookingRequest(
                    user_id=f"user_{i}",
                    item_id=f"item_{i}",
                    date="2026-03-02",
                    timestamp=int(time.time())
                ))
    except:
        pass
    
    print("Прогрев завершен")

def bench_rest_sync():
    # Синхронный REST бенчмарк
    latencies = []
    
    for i in range(REQUESTS_COUNT):
        start = time.time()
        try:
            response = requests.post(REST_URL, json={
                "user_id": f"user_{i}",
                "item_id": f"item_{i}",
                "date": "2026-03-02"
            })
            response.raise_for_status()
            end = time.time()
            latencies.append((end - start) * 1000)
        except Exception as e:
            print(f"REST ошибка: {e}")
    
    return latencies

def bench_rest_concurrent():
    # Конкурентный REST бенчмарк
    
    def make_request(i):
        start = time.time()
        try:
            response = requests.post(REST_URL, json={
                "user_id": f"user_{i}",
                "item_id": f"item_{i}",
                "date": "2026-03-02"
            })
            response.raise_for_status()
            end = time.time()
            return (end - start) * 1000
        except:
            return None
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        latencies = list(executor.map(make_request, range(REQUESTS_COUNT)))
    
    return [l for l in latencies if l is not None]


def bench_grpc():
    # gRPC бенчмарк
    latencies = []
    
    with grpc.insecure_channel(GRPC_ADDR) as channel:
        stub = pb2_grpc.BookingsServiceStub(channel)
        
        for i in range(REQUESTS_COUNT):
            start = time.time()
            try:
                response = stub.CreateBooking(pb2.CreateBookingRequest(
                    user_id=f"user_{i}",
                    item_id=f"item_{i}",
                    date="2026-03-02",
                    timestamp=int(time.time())
                ))
                end = time.time()
                latencies.append((end - start) * 1000)
            except Exception as e:
                print(f"gRPC ошибка: {e}")
    return latencies

def print_stats(name, latencies):
    # Вывод статистики
    if not latencies:
        print(f"{name}: Нет данных")
        return
    
    avg = statistics.mean(latencies)
    median = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]
    p99 = statistics.quantiles(latencies, n=100)[98]
    min_lat = min(latencies)
    max_lat = max(latencies)
    rps = len(latencies) / (sum(latencies) / 1000) if sum(latencies) > 0 else 0
    
    print(f"\n{name}:")
    print(f"  Всего запросов: {len(latencies)}")
    print(f"  Среднее: {avg:.2f} ms")
    print(f"  Медиана: {median:.2f} ms")
    print(f"  P95: {p95:.2f} ms")
    print(f"  P99: {p99:.2f} ms")
    print(f"  Мин: {min_lat:.2f} ms")
    print(f"  Макс: {max_lat:.2f} ms")
    print(f"  RPS: {rps:.0f} req/s")

def test_streaming():
    """Тест Server Streaming метода"""
    print("\n" + "=" * 60)
    print("Тестирование Server Streaming")
    print("=" * 60)
    
    with grpc.insecure_channel(GRPC_ADDR) as channel:
        stub = pb2_grpc.BookingsServiceStub(channel)
        
        # Создаем несколько бронирований для одного пользователя
        user_id = "stream_user"
        for i in range(5):
            stub.CreateBooking(pb2.CreateBookingRequest(
                user_id=user_id,
                item_id=f"item_{i}",
                date="2026-03-02",
                timestamp=int(time.time())
            ))
        
        # Подписываемся на стриминг
        print(f"Подписка на обновления для {user_id}...")
        start = time.time()
        
        responses = stub.SubscribeBookings(pb2.SubscribeRequest(
            user_id=user_id,
            limit=10
        ))
        
        count = 0
        for response in responses:
            count += 1
            print(f"  [{count}] {response.message} (status: {response.status})")
        
        end = time.time()
        print(f"Получено {count} обновлений за {(end - start)*1000:.2f} ms")


def main():
    print("~" * 60)
    print("Бенчмарк: REST vs gRPC")
    print("~" * 60)
    print(f"Project code: bookings-s03")
    print(f"Запросов: {REQUESTS_COUNT}")
    print(f"Конкурентность: {CONCURRENT_WORKERS}")
    print("~" * 60)
    
    warmup()
    
    print("\n" + "~" * 60)
    print("Запуск REST бенчмарка...")
    rest_latencies = bench_rest_sync()
    print_stats("REST (синхронно)", rest_latencies)
    
    print("\n" + "~" * 60)
    print("Запуск конкурентного REST бенчмарка...")
    rest_concurrent = bench_rest_concurrent()
    print_stats("REST (конкурентно)", rest_concurrent)
    
    print("\n" + "~" * 60)
    print("Запуск gRPC бенчмарка...")
    grpc_latencies = bench_grpc()
    print_stats("gRPC", grpc_latencies)
    
    print("\n" + "~" * 60)
    print("Сравнение")
    print("~" * 60)
    
    if rest_latencies and grpc_latencies:
        rest_avg = statistics.mean(rest_latencies)
        grpc_avg = statistics.mean(grpc_latencies)
        speedup = rest_avg / grpc_avg if grpc_avg > 0 else 0
        
        print(f"REST среднее:  {rest_avg:.2f} ms")
        print(f"gRPC среднее:  {grpc_avg:.2f} ms")
        print(f"gRPC быстрее в {speedup:.2f} раз")
    
    test_streaming()

if __name__ == "__main__":
    main()