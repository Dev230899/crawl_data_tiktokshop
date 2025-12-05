from pymongo import MongoClient


class MongoHandler:
    def __init__(self, settings, database_uri=None, database=None):
        self.db_data_lake = settings.DB_DATA_LAKE

        if database_uri and database:
            self.mongo_client = MongoClient(database_uri)[database]
        else:
            self.mongo_client = MongoClient(self.db_data_lake)["crawlerDL"]


class TikTokAccountMongoHandler(MongoHandler):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def insert_tiktok_accounts(self, account):
        collection = self.mongo_client["tiktok_accounts_live_v2"]
        collection.update_one(
            {"url": account["url"]},
            {"$set": account},
            upsert=True,
        )
        print(f"Insert success account: {account}")
