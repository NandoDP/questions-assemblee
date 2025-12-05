from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Configuration de la base de données
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field("questions", env="POSTGRES_DB")
    POSTGRES_USER: str = Field("airflow", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("airflow", env="POSTGRES_PASSWORD")

    # Autres paramètres (API, etc.)
    API_URL: str = Field("https://cms.vie-publique.sn/items/assembly_question", env="API_URL")
    API_TOKEN: Optional[str] = Field(None, env="API_TOKEN")
    API_RATE_LIMIT: int = Field(2000, env="API_RATE_LIMIT")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 