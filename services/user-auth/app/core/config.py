from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str
    HOST: str
    PORT: int

    DATABASE_URL: str = "postgresql://user:password@localhost:5432/student_management"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    MAX_FAILED_LOGIN_ATTEMPTS: int
    LOCK_TIME_LOGIN_WINDOW: int
    LOCK_USER_TIME: int


settings = Settings()
