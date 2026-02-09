from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/hft"
    cors_origins: str = "http://localhost:3000"
    data_provider: str = "yahoo"

    model_config = {"env_prefix": "HFT_"}

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS origins from a comma-separated string.

        Supports: "*", "https://a.com", "https://a.com,https://b.com"
        """
        return [o.strip().rstrip("/") for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
