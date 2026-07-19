SCRIPT_DIR=$(cd $(dirname $0); pwd)

# Activate the virtual environment
source $SCRIPT_DIR/.venv/bin/activate

# Wait for the docker to be ready
echo "Waiting for Docker to be ready..."
until docker info > /dev/null 2>&1; do
	sleep 1
done

# Start psql container
# Check if the container is already running
if [ "$(docker ps -q -f name=my-postgres)" ]; then
	echo "PostgreSQL container is already running."
else
	echo "Starting PostgreSQL container..."
	docker run --name my-postgres \
				-p 5432:5432 \
				-e POSTGRES_USER=user \
				-e POSTGRES_PASSWORD=password \
				-e POSTGRES_DB=dbname \
				-d postgres
fi

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
until docker exec my-postgres pg_isready -U user > /dev/null 2>&1; do
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

# Start the FastAPI server
cd $SCRIPT_DIR
uvicorn app.main:app --host 0.0.0.0 --port 8000
