# REST нагрузочное тестирование для events-s03

echo "========================================="
echo "REST Load Testing for events-s03"
echo "========================================="

# Параметры
URL="http://localhost:8000/events"
DURATION="30s"

# Тест с разным количеством соединений
for CONN in 1 10 100 500
do
    echo ""
    echo "--- Testing with $CONN connections ---"
    wrk -t$CONN -c$CONN -d$DURATION --latency $URL
    echo "----------------------------------------"
done

# Тест POST запросов
echo ""
echo "--- Testing POST requests ---"
wrk -t10 -c10 -d$DURATION --latency \
    -s <(echo '
    wrk.method = "POST"
    wrk.body   = "{\"name\":\"test\",\"location\":\"Moscow\"}"
    wrk.headers["Content-Type"] = "application/json"
    ') $URL