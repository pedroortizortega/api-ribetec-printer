from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    host_ribetec_printer: str = "192.168.100.5"
    printer_port: int = 9100
    app_title: str = "Ribetec Printer API"
    app_version: str = "1.0.0"

    # DB (PostgreSQL / RDS). Puedes definir DATABASE_URL completo o los campos sueltos.
    # Ejemplo DATABASE_URL:
    #   postgresql://user:password@host:5432/dbname?sslmode=require
    database_url: str | None = os.getenv("DATABASE_URL")
    db_host: str | None = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_user: str | None = os.getenv("DB_USER")
    db_password: str | None = os.getenv("DB_PASSWORD")
    db_name: str | None = os.getenv("DB_NAME")
    db_sslmode: str = os.getenv("DB_SSLMODE", "prefer")
    logger.info(f"db_host: {db_host}")
    logger.info(f"db_port: {db_port}")
    logger.info(f"db_user: {db_user}")
    logger.info(f"db_password: {db_password}")
    logger.info(f"db_name: {db_name}")
    logger.info(f"db_sslmode: {db_sslmode}")

    # @property
    def resolved_database_url(self) -> str | None:
        """Devuelve DATABASE_URL si existe, si no construye un DSN con DB_*."""
        if self.database_url:
            return self.database_url

        if not (self.db_host and self.db_user and self.db_password and self.db_name):
            return None
        logger.info(f"db_host: {self.db_host}")
        logger.info(f"db_port: {self.db_port}")
        logger.info(f"db_user: {self.db_user}")
        logger.info(f"db_password: {self.db_password}")
        logger.info(f"db_name: {self.db_name}")
        logger.info(f"db_sslmode: {self.db_sslmode}")
        user = quote(self.db_user, safe="")
        password = quote(self.db_password, safe="")
        host = self.db_host
        port = self.db_port
        dbname = quote(self.db_name, safe="")
        sslmode = quote(self.db_sslmode, safe="")

        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
