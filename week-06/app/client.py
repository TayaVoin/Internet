import requests
import json
from typing import Dict, Any, Optional

def build_payload(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Формирует словарь для отправки GraphQL запроса.
    :param query: Текст запроса (query или mutation)
    :param variables: Словарь с переменными (по умолчанию None)
    :return: Словарь с ключами "query" и "variables"
    """
    payload = {"query": query}
    
    if variables:
        payload["variables"] = variables
    
    return payload

def send_graphql_request(
    url: str,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Отправляет GraphQL запрос на сервер и возвращает ответ.
    :param url: URL GraphQL эндпоинта
    :param query: Текст запроса
    :param variables: Переменные запроса
    :param headers: Дополнительные заголовки
    :return: Ответ сервера в виде словаря
    """
    # Формируем заголовки
    if headers is None:
        headers = {}
    
    # Добавляем Content-Type
    if "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
    
    # Формируем payload
    payload = build_payload(query, variables)
    
    try:
        # Отправляем запрос
        response = requests.post(url, json=payload, headers=headers)
        
        # Проверяем HTTP статус
        if response.status_code != 200:
            print(f"HTTP ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return {"errors": [{"message": f"HTTP {response.status_code}"}]}
        
        # Парсим JSON ответ
        result = response.json()
        
        # Проверяем наличие ошибок в ответе
        if "errors" in result:
            print("GraphQL ошибки:")
            for error in result["errors"]:
                print(f"  - {error.get('message', 'Unknown error')}")
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"Ошибка подключения к {url}")
        return {"errors": [{"message": "Connection error"}]}
    except requests.exceptions.Timeout:
        print("Таймаут запроса")
        return {"errors": [{"message": "Request timeout"}]}
    except json.JSONDecodeError:
        print("Ошибка парсинга JSON ответа")
        return {"errors": [{"message": "Invalid JSON response"}]}
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return {"errors": [{"message": str(e)}]}

def example_queries():
    url = "http://localhost:8239/graphql"
    
    print("~" * 60)
    print("G R A P H Q L   К Л И Е Н Т   Д Л Я   L O G S")
    print("~" * 60)
    print(f"Project code: logs-s03")
    print(f"Endpoint: {url}")
    print("~" * 60)
    
    print("\nQUERY: получить все логи")
    query_logs = """
    query {
        logs {
            id
            message
            level
            timestamp
        }
    }
    """
    
    result = send_graphql_request(url, query_logs)
    if "data" in result:
        print("Ответ получен:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    else:
        print("Не удалось получить данные")
    
    print("\nMUTATION: создать лог")
    mutation_create = """
    mutation($message: String!, $level: String!) {
        createLog(message: $message, level: $level) {
            id
            message
            level
            timestamp
        }
    }
    """
    variables = {
        "message": "Тестовое сообщение",
        "level": "INFO"
    }
    
    result = send_graphql_request(url, mutation_create, variables)
    if "data" in result:
        print("Лог создан:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    else:
        print("Не удалось создать лог")
    
    print("\nQUERY: получить лог по ID")
    query_by_id = """
    query($id: ID!) {
        log(id: $id) {
            id
            message
            level
            timestamp
        }
    }
    """
    variables = {"id": "1"}
    
    result = send_graphql_request(url, query_by_id, variables)
    if "data" in result and result["data"].get("log"):
        print("Лог найден:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    else:
        print("Лог с ID 1 не найден (возможно, еще не создан)")
    
    print("\nQUERY: пример с ошибкой (неправильный тип)")
    query_with_error = """
    query($id: Int!) {
        log(id: $id) {
            id
            message
        }
    }
    """
    variables = {"id": "not_a_number"}  # Неправильный тип
    
    result = send_graphql_request(url, query_with_error, variables)
    if "errors" in result:
        print("Ошибка обработана корректно")

def main():
    """Основная функция для запуска примеров"""
    example_queries()
    
    print("\n" + "~" * 60)
    print("Инструкция по использованию:")
    print("~" * 60)
    print("1. Убедитесь, что GraphQL сервер запущен на порту 8239")
    print("2. Импортируйте функции в свой код:")
    print("   from app.client import build_payload, send_graphql_request")
    print("3. Используйте build_payload для формирования запроса")
    print("4. Используйте send_graphql_request для отправки")

if __name__ == "__main__":
    main()