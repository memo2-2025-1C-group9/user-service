import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.routers.user_router import router as user_router
from app.utils.problem_details import problem_detail_response
from app.core.auth import get_service_auth
from contextlib import asynccontextmanager
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa los servicios necesarios al arrancar la aplicación"""
    environment = settings.ENVIRONMENT

    if environment != "test":
        service_auth = get_service_auth()
        await service_auth.initialize()
        logging.info("Servicio de autenticación inicializado")
    else:
        logging.info("Modo test: se omite autenticación del servicio")
    yield


app = FastAPI(lifespan=lifespan)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Determinar el título basado en el código de status
    title = "Error de Servidor"
    if exc.status_code == 401:
        title = "No Autorizado"
    elif exc.status_code == 403:
        title = "Prohibido"
    elif exc.status_code == 404:
        title = "No Encontrado"
    elif exc.status_code == 400:
        title = "Solicitud Incorrecta"
    elif exc.status_code == 422:
        title = "Error de Validación"
    elif exc.status_code < 500:
        title = "Error de Cliente"

    logging.error(
        f"HTTPException manejada: {exc.detail} (status: {exc.status_code}, url: {request.url})"
    )

    headers = exc.headers or {}

    headers["Content-Type"] = "application/problem+json"

    headers["Access-Control-Allow-Origin"] = "*"

    return problem_detail_response(
        status_code=exc.status_code,
        title=title,
        detail=exc.detail,
        instance=str(request.url),
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"Error de validación: {exc.errors()} (url: {request.url})")

    headers = {
        "Content-Type": "application/problem+json",
        "Access-Control-Allow-Origin": "*",
    }

    return problem_detail_response(
        status_code=422,
        title=exc.errors()[0]["type"],
        detail=exc.errors()[0]["msg"],
        instance=str(request.url),
        headers=headers,
    )


app.include_router(user_router)


@app.get("/health")
def get_health():
    return {"status": "ok"}
