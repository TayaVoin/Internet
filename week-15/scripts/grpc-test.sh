# gRPC нагрузочное тестирование для events-s03

echo "========================================="
echo "gRPC Load Testing for events-s03"
echo "========================================="

# Параметры
PROTO="weeks/week-08/proto/service.proto"
ADDR="localhost:50051"
DURATION="30s"
TOTAL_REQUESTS=10000

# Unary метод GetEvent
echo ""
echo "--- Testing Unary RPC GetEvent ---"
ghz --insecure \
    --proto $PROTO \
    --call events.v1.EventsService.GetEvent \
    -d '{"id":"1"}' \
    -c 10 \
    -n $TOTAL_REQUESTS \
    $ADDR

# Unary метод CreateEvent
echo ""
echo "--- Testing Unary RPC CreateEvent ---"
ghz --insecure \
    --proto $PROTO \
    --call events.v1.EventsService.CreateEvent \
    -d '{"name":"Test Event","location":"Moscow"}' \
    -c 10 \
    -n $TOTAL_REQUESTS \
    $ADDR

# Тест с разной конкурентностью
for CONN in 1 10 50 100
do
    echo ""
    echo "--- Testing with $CONN connections ---"
    ghz --insecure \
        --proto $PROTO \
        --call events.v1.EventsService.GetEvent \
        -d '{"id":"1"}' \
        -c $CONN \
        -n $((10000 * CONN)) \
        --duration $DURATION \
        $ADDR
done