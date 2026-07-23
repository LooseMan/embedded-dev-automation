
ENDPOINT="http://localhost:8000/good_sleep"

for i in $(seq 1 5); do
    echo "Sending request $i..."
    curl    -X POST "$ENDPOINT" \
            -H "Content-Type: application/json" \
            -d '{"a": 0, "b": 0}' &
    echo "Request $i sent."
done
