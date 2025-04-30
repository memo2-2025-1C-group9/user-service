from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )

    ENVIRONMENT: str
    HOST: str
    PORT: int

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    PGSSLMODE: str = "require"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.PGSSLMODE}"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    MAX_FAILED_LOGIN_ATTEMPTS: int
    LOCK_TIME_LOGIN_WINDOW: int
    LOCK_USER_TIME: int

    SERVICE_USERNAME: str
    SERVICE_PASSWORD: str
    SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES: int

try:
    settings = Settings()
    logger.debug("Configuración cargada exitosamente")
    logger.debug(f"HOST: {settings.HOST}")
    logger.debug(f"DB_HOST: {settings.DB_HOST}")
    logger.debug(f"DB_PORT: {settings.DB_PORT}")
    logger.debug(f"DATABASE_URL: {settings.DATABASE_URL}")
except Exception as e:
    logger.error(f"Error al cargar la configuración: {str(e)}")
    raise
