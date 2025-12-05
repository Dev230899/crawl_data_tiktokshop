from enum import Enum
from pydantic import BaseModel
from typing import Any


class CrawlManagerJob(BaseModel):
    domain: str | None  # domain job
    url: str | None  # url được của job
    total_crawled_urls: int | None  # tổng số urls crawl được
    total_founded_urls: int | None  # tổng số urls phát hiện
    crawled_time: float | None  # thời gian hoàn thành


class FrontierCheck(str, Enum):
    CHECK = "CHECK"
    PASS = "PASS"
    STOP = "STOP"


class CrawlJob(BaseModel):
    domain: str  # EX: domain job
    url: str
    storage_topic: str  # topic lưu trữ dữ liệu
    frontier_check: FrontierCheck = FrontierCheck.CHECK

    extend_config: dict = {}


class BaseData(BaseModel):
    url: str

    class Config:
        allow_population_by_field_name = True
    

class Category(BaseModel):
    id: str = None
    name: str | None
    url: str | None


class Shop(BaseModel):
    shop_id: str | None
    url: str | None
    name: str | None
    location: str | None
    rating: str | None | int | float
    is_official: bool | None


class Product(BaseData):
    domain: str
    category_id: str | None
    product_id: str
    product_sku: str | None
    name: str | None = None
    images: list[str] | None
    videos: list[str] | None
    price: int | str | None
    price_before_discount: int | str | None
    price_range: list | str | None
    price_range_before_discount: list | str | None
    rating_star: str | int | float = None
    rating_count: int | str | None
    liked_count: str | int | None
    descriptions: str | list[str] | None
    crawl_category_name: str | None
    crawl_category_key: str | None
    crawl_category_url: str | None
    sub_categories: list[Category] | None
    quantity_sold: int | str | None
    stock: int | str | None
    shop: Shop | None
    is_adult: bool | None
    currency: str | None

    product_options: list[dict] | None


class TiktokShop(BaseData):
    url: str
    shop_name: str
    rating: str | None
    following: float | None
    followers: float | None
    likes: float | None
    phones: list | None
    bio: str | None
    facebook_info: dict | None
    zalo_info: dict | None
    products: list | None
