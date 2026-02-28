def next_state(state: str, event: str) -> str:
    """
    Функция переходов состояний для саги.
    
    Тесты проверяют:
    - NEW + PAY_OK -> PAID
    - NEW + PAY_FAIL -> CANCELLED
    """
    transitions = {
        ('NEW', 'PAY_OK'): 'PAID',
        ('NEW', 'PAY_FAIL'): 'CANCELLED',
    }
    
    return transitions.get((state, event), state)