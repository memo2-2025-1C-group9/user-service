#!/bin/bash

sudo docker-compose down

# Asegurarse de que la base de datos esté corriendo
sudo docker-compose up -d db

# Ejecutar los tests y generar el reporte de coverage
sudo docker-compose --profile test run --rm test bash -c "coverage run -m pytest tests/ && coverage report -m" 