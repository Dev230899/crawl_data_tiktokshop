import pathlib

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # redis connection
    REDIS_URL: str = (
        "redis://:7tS1ZosMDzTWBWqK@redis-master.redis.svc.cluster.local:6379/0"
    )

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka.crawl.tmtco.org:9092"

    # mongo connection
    DB_DATA_LAKE: str = (
        "mongodb+srv://dev-crawler:2OPKYWjHWtZWGR@rscrawl.mdb.crawl.tmtco.org/crawlerDL?authMechanism=SCRAM-SHA-256&authSource=crawlerDL&ssl=false"
    )
    DB_DATA_WARE_HOUSE: str = (
        "mongodb+srv://dev-crawler:2OPKYWjHWtZWGR@rscrawl.mdb.crawl.tmtco.org/crawlerDW?authMechanism=SCRAM-SHA-256&authSource=crawlerDW&ssl=false"
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
