from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    @field_validator("cors_origins", mode="after")
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        if "*" in v:
            raise ValueError(
                "Wildcard CORS origin '*' is not allowed when credentials are enabled."
            )
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Talent Marketplace API"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/talent_db"
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json

                return json.loads(v)
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
