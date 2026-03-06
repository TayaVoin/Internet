# Простой тест для проверки клиента без запуска сервера

from client import build_payload

def test_build_payload():
    """Тестируем функцию build_payload"""
    
    # Тест 1: только query
    payload = build_payload("query { ping }")
    assert "query" in payload
    assert payload["query"] == "query { ping }"
    assert "variables" not in payload
    print("Тест 1 пройден: только query")
    
    # Тест 2: query + variables
    payload = build_payload(
        "query($id: ID!) { log(id: $id) { message } }",
        {"id": 123}
    )
    assert "query" in payload
    assert "variables" in payload
    assert payload["variables"]["id"] == 123
    print("Тест 2 пройден: query + variables")
    
    # Тест 3: проверка project_code
    with open("client.py", "r") as f:
        content = f.read()
        assert "logs-s03" in content
        print("Тест 3 пройден: project_code найден")
    
    print("\nВсе тесты пройдены!")

if __name__ == "__main__":
    test_build_payload()