from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    host_ribetec_printer: str = "192.168.100.5"
    printer_port: int = 9100
    app_title: str = "Ribetec Printer API"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
