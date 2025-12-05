from pymongo import MongoClient
from pymongo import DESCENDING


class MongoHandler:
    def __init__(self, settings, database_uri=None, database=None):
        self.db_data_ware_house = settings.DB_DATA_LAKE

        if database_uri and database:
            self.mongo_client = MongoClient(database_uri)[database]
        else:
            self.mongo_client = MongoClient(self.db_data_ware_house)["crawlerDL"]


class TiktokVideoMongoHandler(MongoHandler):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def get_tiktok_user(self):
        collection = self.mongo_client["tiktok_accounts_live_v2"]
        return collection.find({"CommentsFetched": {"$exists": False}}).batch_size(10)

    def check_exists(self, post_url):
        collection = self.mongo_client["tiktok_post_comments"]
        item = collection.find({"post_url": post_url})
        if item:
            return True
        return False

    def insert_post_comments(self, post):
        collection = self.mongo_client["tiktok_post_comments"]
        collection.update_one(
            {"post_url": post["post_url"]},
            {
                "$setOnInsert": {
                    "post_url": post["post_url"],
                    "author_name": post["author_name"],
                    "post_date": post["post_date"],
                    "post_title": post["post_title"],
                    "author_profile_link": post["author_profile_link"],
                    "category": post["category"],
                },
                "$addToSet": {"comments": {"$each": post["comments"]}},
                "$set": {"crawl_date": post["crawl_date"]},
            },
            upsert=True,
        )
        print(f"Insert success post comments: {post}")

class TiktokShopMongoHandler(MongoHandler):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def insert_product(self, product):
        if not isinstance(product, dict):
            product = product.dict()
        collection = self.mongo_client["ecommerce-products"]
        collection.update_one({"url": product["url"]}, {"$set": product}, upsert=True)
        print("insert product successfully:", product)

    def inser_shop(self, shop):
        if not isinstance(shop, dict):
            shop = shop.dict()
        collection = self.mongo_client["tiktokshop"]
        collection.update_one(
            {"url": shop["url"]},
            {
                "$setOnInsert": {
                    "url": shop["url"],
                    "shop_name": shop["shop_name"],
                    "rating": shop["rating"],
                    "following": shop["following"],
                    "followers": shop["followers"],
                    "likes": shop["likes"],
                    "phones": shop["phones"],
                    "bio": shop["bio"],
                    "facebook_info": shop["facebook_info"],
                    "zalo_info": shop["zalo_info"],
                },
                "$addToSet": {"products": {"$each": shop["products"]}},
            },
            upsert=True,
        )
        print("insert shop successfully:", shop)

        