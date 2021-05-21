from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    SERVICE_NAME: str = "Flat price statistic"

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 5000

    DEBUG: bool = True

    DB_NAME: str = "ads"
    DB_URL: str = "mongodb://localhost:27018/"
