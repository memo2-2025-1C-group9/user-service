from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # Service Authentication
    SERVICE_USERNAME: str
    SERVICE_PASSWORD: str

    # API settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    ENVIRONMENT: str = "development"

    AUTH_SERVICE_URL: str

    model_config = ConfigDict(env_file=".env")


settings = Settings()
