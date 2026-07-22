SCRIPT_DIR=$(cd $(dirname $0); pwd)

# Wait for the docker to be ready
echo "Waiting for Docker to be ready..."
until docker info > /dev/null 2>&1; do
	sleep 1
done

# Create container network
CONTAINER_NETWORK="web-back-network"
docker network create "$CONTAINER_NETWORK"

# Start psql container
DB_CONTAINER="my-postgres"
docker rm -f "${DB_CONTAINER}"

if docker ps -q -f "name=^${DB_CONTAINER}$" | grep -q .; then
    echo "PostgreSQL container is already running."

elif docker ps -aq -f "name=^${DB_CONTAINER}$" | grep -q .; then
    echo "Starting existing PostgreSQL container..."
    docker start "${DB_CONTAINER}"

else
    echo "Creating PostgreSQL container..."
    docker run --name "${DB_CONTAINER}" \
        -p 5432:5432 \
		--network "$CONTAINER_NETWORK" \
        -e POSTGRES_USER=user \
        -e POSTGRES_PASSWORD=password \
        -e POSTGRES_DB=dbname \
        -d postgres
fi

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
until docker exec "${DB_CONTAINER}" pg_isready -U user > /dev/null 2>&1; do
	sleep 1
done
echo "Database is ready!"

# Open the FastAPI server in the default web browser
if command -v xdg-open > /dev/null; then
	# for Linux
	xdg-open http://localhost:8000/docs
elif command -v open > /dev/null; then
	# for macOS
	open http://localhost:8000/docs
else
	echo "Please open http://localhost:8000 in your web browser."
fi

# Start api container
API_CONTAINER="my-fastapi"
docker rm -f "${API_CONTAINER}"

if docker ps -q -f "name=^${API_CONTAINER}$" | grep -q .; then
    echo "FastAPI container is already running."

elif docker ps -aq -f "name=^${API_CONTAINER}$" | grep -q .; then
    echo "Starting existing FastAPI container..."
    docker start "${API_CONTAINER}"

else
    echo "Creating FastAPI container..."
    docker run --name "${API_CONTAINER}" \
        -p 8000:8000 \
		--network "$CONTAINER_NETWORK" \
		-e DATABASE_URL="postgresql+asyncpg://user:password@${DB_CONTAINER}:5432/dbname" \
		-d fastapi-app
fi
