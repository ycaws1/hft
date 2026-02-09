from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/hft"
    cors_origins: list[str] = ["http://localhost:3000"]
    data_provider: str = "yahoo"

    model_config = {"env_prefix": "HFT_"}


settings = Settings()
