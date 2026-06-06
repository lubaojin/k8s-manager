from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "K8s Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # MySQL
    DB_HOST: str = "192.168.3.31"
    DB_PORT: int = 3307
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "k8s_manager"

    # JWT
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
