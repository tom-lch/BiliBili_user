import pymongo

def store_MongoDB(item):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client.bilibili_user20
    collection = db.user_info
    collection.insert_one(item)
