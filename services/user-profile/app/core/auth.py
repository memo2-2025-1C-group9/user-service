import httpx
import logging
from typing import Optional
from functools import lru_cache
from app.core.config import settings


class ServiceAuth:
    def __init__(self):
        self.base_url = settings.AUTH_SERVICE_URL
        self.access_token: Optional[str] = None

    async def initialize(self) -> None:
        """Inicializa la autenticación del servicio"""
        if not self.access_token:
            await self.login()

    async def login(self) -> Optional[str]:
        """Obtiene un token de acceso usando las credenciales del servicio"""
        try:
            async with httpx.AsyncClient() as client:
                logging.info("Intentando autenticar servicio...")
                logging.debug(f"URL: {self.base_url}/token/service")
                logging.debug(f"Username: {settings.SERVICE_USERNAME}")

                response = await client.post(
                    f"{self.base_url}/token/service",
                    data={
                        "username": settings.SERVICE_USERNAME,
                        "password": settings.SERVICE_PASSWORD,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                # Loguear la respuesta completa para debugging
                logging.debug(
                    f"Respuesta del servicio: Status={response.status_code}, Body={response.text}"
                )

                if response.status_code == 200:
                    self.access_token = response.json()["access_token"]
                    logging.info("Servicio autenticado exitosamente")
                    return self.access_token
                else:
                    logging.error(
                        f"Error en la autenticación del servicio. Status: {response.status_code}"
                    )
                    logging.error(f"URL: {self.base_url}/token/service")
                    logging.error(f"Detalle del error: {response.text}")
                    return None

        except Exception as e:
            logging.error(f"Error al intentar autenticar el servicio: {str(e)}")
            logging.error(f"URL: {self.base_url}/token/service")
            return None

    def get_token(self) -> Optional[str]:
        """Retorna el token actual"""
        return self.access_token


@lru_cache()
def get_service_auth() -> ServiceAuth:
    """Singleton para obtener la instancia de ServiceAuth"""
    return ServiceAuth()
