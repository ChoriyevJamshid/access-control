# AccessControl local development.
#
#   make setup   create backend venv, install backend/frontend dependencies, apply migrations
#   make run     start Redis (Docker, unless 6379 is already taken), Django, Celery worker, Celery beat, Vite
#
# On Windows (GNU Make: `choco install make`) both targets delegate to run.ps1,
# which opens every service in its own window.

.PHONY: run setup

ifeq ($(OS),Windows_NT)

RUN_PS := powershell -NoProfile -ExecutionPolicy Bypass -File run.ps1

run:
	$(RUN_PS)

setup:
	$(RUN_PS) -Setup

else

# Relative to backend/: every backend recipe starts with `cd backend`.
PY              := venv/bin/python
REDIS_CONTAINER := access-control-redis
REDIS_UP        := python3 -c "import socket; socket.create_connection(('127.0.0.1', 6379), 1)"

.PHONY: redis backend celery beat frontend

# Ctrl+C stops all four processes.
run: redis
	@$(MAKE) --no-print-directory -j4 backend celery beat frontend

setup:
	cd backend && (test -x $(PY) || python3 -m venv venv)
	cd backend && $(PY) -m pip install -r requirements/base.txt
	cd backend && $(PY) manage.py migrate
	cd frontend && npm install

redis:
	@if $(REDIS_UP) 2>/dev/null; then \
		echo "Redis is already listening on 6379"; \
	else \
		docker start $(REDIS_CONTAINER) >/dev/null 2>&1 || \
		docker run -d --name $(REDIS_CONTAINER) -p 127.0.0.1:6379:6379 redis:7 >/dev/null; \
	fi

backend:
	cd backend && $(PY) manage.py runserver

celery:
	cd backend && $(PY) -m celery -A src worker -l INFO

beat:
	cd backend && $(PY) -m celery -A src beat -l INFO

frontend:
	cd frontend && npm run dev

endif
