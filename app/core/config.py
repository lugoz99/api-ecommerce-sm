from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DB_DRIVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # let's ignore extar parameters
        extra = "ignore"


settings = Settings()
