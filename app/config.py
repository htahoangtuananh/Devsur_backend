from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./devsur.db"
    API_TITLE: str = "Devsur API"
    API_VERSION: str = "1.0.0"
    DEFAULT_USER_ID: str = "default"
    PACK_SIZE: int = 5
    DAILY_PACK_SEED: int = 42

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()