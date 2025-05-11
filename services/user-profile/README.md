# User Profile Service

Servicio para editar y actualizar información del perfil de usuario.

## Requisitos
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
cd  user-profile
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



