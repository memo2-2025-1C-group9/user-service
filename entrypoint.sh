#!/bin/bash

# Establecer PYTHONPATH para que pytest encuentre el módulo app
export PYTHONPATH=/app

# Iniciar la aplicación FastAPI en segundo plano
uvicorn app.main:app --host $HOST --port $PORT &
UVICORN_PID=$!

# Ejecutar las pruebas de pytest
pytest tests -q --continue-on-collection-errors --capture=no
TEST_EXIT_CODE=$?

# Mostrar un mensaje que indique si las pruebas son exitosas o si hay algunas fallidas
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "Las pruebas pasaron exitosamente."
else
    echo "Algunas pruebas fallaron. Verifica los resultados."
fi

# Esperar a que el proceso de uvicorn termine
wait $UVICORN_PID

# Salir con el código de salida de pytest
exit $TEST_EXIT_CODE