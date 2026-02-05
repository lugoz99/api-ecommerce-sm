from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_DRIVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    API_SECRET: str
    API_KEY: str
    CLOUD_NAME: str
    CLOUDINARY_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # permite que si hay más cosas en el .env no explote
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
