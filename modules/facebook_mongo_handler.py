from pymongo import MongoClient
from pymongo import DESCENDING


class MongoHandler:
    def __init__(self, settings, database_uri=None, database=None):
        self.db_data_ware_house = settings.DB_DATA_WARE_HOUSE

        if database_uri and database:
            self.mongo_client = MongoClient(database_uri)[database]
        else:
            self.mongo_client = MongoClient(self.db_data_ware_house)["crawlerDW"]


class FacebookFanpagesMongoHandler(MongoHandler):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def update_facebook_account(self, fanpage_url, item):
        try:
            collection = self.mongo_client["ads_facebook_fanpages"]
            if item is None:
                collection.update_one(
                    {"pageUrl": fanpage_url}, {"$set": {"Fetched": True}}
                )
            else:
                collection.update_one(
                    {"pageUrl": fanpage_url}, {"$set": {"Info": item, "Fetched": True}}
                )
                print("update facebook account:", item)
        except Exception as exc:
            print("error:", exc)

    def get_facebook_fanpages(self):
        try:
            collection = self.mongo_client["ads_facebook_fanpages"]
            return collection.aggregate(
                [
                    {
                        "$match": {
                            "Info": {"$exists": False},
                            "Fetched": {"$exists": False},
                        }
                    },
                    {"$sort": {"crawledAt": -1}},
                    {"$project": {"_id": 0, "pageUrl": 1}},
                    {"$sample": {"size": 1000}},
                ]
            )
        except Exception as exc:
            print("error:", exc)
            return []

    def get_url_fanpage(self):
        collection = self.mongo_client["ads_facebook_fanpages"]
        return (
            collection.find(
                {"Info": {"$exists": True}, "CommentsFetched": {"$exists": False}}
            )
            .sort("crawledAt", DESCENDING)
            .batch_size(1000)
        )

    def insert_post_comments(self, post):
        collection = self.mongo_client["facebook_post_comments"]
        collection.update_one(
            {"post_url": post["post_url"]},
            {"$set": post},
            upsert=True,
        )

        ads_face_collection = self.mongo_client["ads_facebook_fanpages"]
        ads_face_collection.update_one(
            {"pageId": post["fanpage_id"]},
            {"$set": {"CommentsFetched": True}},
        )

        print(f"Insert success post comments: {post}")
