#!/bin/sh

set -e

echo "Aguardando o banco de dados inicializar..."

poetry run alembic upgrade head

poetry run uvicorn --host 0.0.0.0 --port 8000 fastapi.app:app 