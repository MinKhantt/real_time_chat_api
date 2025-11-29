from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@db:5432/{self.DB_NAME}"

    # API settings
    # Add default values to formerly required fields
    API_PREFIX: str = "/api" 
    API_V1: str = "/v1"
    DEBUG: bool = False
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "your-insecure-default-secret-key-change-this-in-env"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()