# ClassConnect Template Service


[![CI/CD Pipeline](https://github.com/memo2-2025-1C-group9/template-service/actions/workflows/cicd.yml/badge.svg)](https://github.com/memo2-2025-1C-group9/student-management/actions/workflows/cicd.yml)


## Tabla de Contenido
1. Introduccion
2. Requisitos Previos
3. Requisitos
4. Instalacion
5. Run
6. FastAPI Links
7. Pytest Links

## Introduccion
Bienvenido a ClassConnect!

En nuestra plataforma de aprendizaje de la proxima generacion
podras crear, editar y eliminar tus cursos como mejor te parezca.
Cada curso tendra titulo y descripcion y podras consultarlos cuando gustes!

## Requisitos Previos
- Python 3
- Docker

## Requisitos (incluidos en el Dockerfile)
- FastAPI: Framework para contruir la API.
- Uvicorn: Servidor para ejecutar FastAPI.
- Pydantic: Manejar y validar modelos de datos usados.
- Pytest: Framewor de testing de Python.

Se pueden instalar localmente en caso de no usar el Dockerfile:
```sh
pip install -r requirements.txt
```

## Instalacion
1. Clonar el Repo:
```sh
git clone https://github.com/florenciavillar/template-service.git
cd  template-service
```

2. Crear el env development a partir del example:
```sh
cp .env.example .env.development
```

## Run
```sh
docker-compose up --build
```

## FastAPI Links
Puedes probar endpoints en FastAPI

http://localhost:8080/docs#/

Ver mas documentacion de endpoints aca! http://localhost:8080/redoc

## Pytest Links
user-guide: https://docs.pytest.org/en/stable/how-to/index.html
fixture: https://docs.pytest.org/en/stable/reference/fixtures.html#fixtures
