# ===== RUNNING THE APPLICATION =====

# Method 1: Local Development (3 separate terminals)

# Terminal 1: Start Redis (if not using Docker)
redis-server

# Terminal 2: Start FastAPI
uvicorn main:app --reload --port 8000

# Terminal 3: Start Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 4: Start Celery Beat (scheduler) 
celery -A celery_app beat --loglevel=info

# Method 2: Using Docker Compose (simplest)
docker-compose up

# Method 3: Combined Celery command (development only)
celery -A celery_app worker --beat --loglevel=info

# ===== TESTING =====

# Check if everything is running:
curl http://localhost:8000/health

# Trigger manual tasks:
curl -X POST http://localhost:8000/tasks/update-files
curl -X POST http://localhost:8000/tasks/generate-report

# Check task status:
curl http://localhost:8000/tasks/{task_id}/status

# List scheduled tasks:
curl http://localhost:8000/tasks/scheduled