from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    app_name: str = "Gymsense API"
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "phi3:mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()