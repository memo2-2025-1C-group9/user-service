#!/bin/bash

# Establecer PYTHONPATH para que pytest encuentre el módulo app
export PYTHONPATH=/app

# Si estamos en modo test, ejecutamos los tests
if [ "$2" = "test" ]; then
    export TESTING=1
    # Ejecutar los tests con coverage y sin captura de salida
    pytest tests/ -v --cov=app --cov=tests --cov-report=term-missing --capture=no
    exit $?
fi

# Si no estamos en modo test, iniciamos la aplicación FastAPI
if [ "$2" = "app" ]; then
    export TESTING=0
    gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind "$HOST:$PORT"
fi