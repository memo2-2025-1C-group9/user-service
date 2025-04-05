#!/bin/bash

# Establecer PYTHONPATH para que pytest encuentre el módulo app
export PYTHONPATH=/app

# Iniciar la aplicación FastAPI
uvicorn app.main:app --host $HOST --port $PORT &

UVICORN_PID=$!

# Ejecutar las pruebas de pytest automaticamente al levantar el container
# Sigo corriendo FastAPI independientemente del resultado de las pruebas
# Dasabilito capture para que permita el logging de pytest
pytest tests -q --continue-on-collection-errors --capture=no

# Mostrar un mensaje que indique si las pruebas son exitosas o si hay algunas fallidas
if [ $? -eq 0 ]; then
    echo "Las pruebas pasaron exitosamente."
else
    echo "Algunas pruebas fallaron. Verifica los resultados."
fi

wait $UVICORN_PID
