import pathlib

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # redis connection
    REDIS_URL: str = (
        ""
    )

    KAFKA_BOOTSTRAP_SERVERS: str = ""

    # mongo connection
    DB_DATA_LAKE: str = (
        ""
    )
    DB_DATA_WARE_HOUSE: str = (
        ""
    )
    # minio connection, lưu trữ file, ảnh
    MINIO_URL: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "12345678"
    MINIO_BUCKET_NAME: str = "tmt-dn"

    SELENIUM_TYPE: str = "LOCAL"  # "LOCAL"
    SELENIUM_GRID_URL: str = (
        "http://selenium-router.selenium.svc.cluster.local:4444/wd/hub"
    )

    class Config:
        env_file = f"{pathlib.Path(__file__).resolve().parent}/.env"
        env_file_encoding = "utf-8"


settings = Settings()
