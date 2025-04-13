from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    ENVIRONMENT: str
    HOST: str
    PORT: int

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require",
    )

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    MAX_FAILED_LOGIN_ATTEMPTS: int
    LOCK_TIME_LOGIN_WINDOW: int
    LOCK_USER_TIME: int


settings = Settings()
