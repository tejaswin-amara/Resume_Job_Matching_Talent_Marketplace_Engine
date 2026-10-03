from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Talent Marketplace API"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/talent_db"

    class Config:
        env_file = ".env"


settings = Settings()
