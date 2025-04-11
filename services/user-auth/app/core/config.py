from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str
    HOST: str
    PORT: int

    DATABASE_URL: str = "postgresql://user:password@localhost:5432/student_management"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings = Settings()
