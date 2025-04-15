#!/bin/bash

# Establecer PYTHONPATH para que pytest encuentre el módulo app
export PYTHONPATH=/app

# Verificar si se proporcionó un argumento
if [ "$1" = "test" ]; then
    echo "Ejecutando tests..."
    pytest tests/
elif [ "$1" = "app" ]; then
    echo "Iniciando la aplicación..."
    uvicorn app.main:app --host $HOST --port $PORT
else
    echo "Uso: /entrypoint.sh [test|app]"
    exit 1
fi