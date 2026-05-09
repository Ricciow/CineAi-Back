import pymongo
from src.core.config import settings

is_cloud = "mongodb+srv" in settings.DATABASE_URL or "ssl=true" in settings.DATABASE_URL.lower()

mongo_args = {
    "host": settings.DATABASE_URL,
    "retryWrites": False,
}

if "," in settings.DATABASE_URL:
    mongo_args["host"] = settings.DATABASE_URL.split(",")

if is_cloud:
    mongo_args["tls"] = True
    mongo_args["tlsAllowInvalidCertificates"] = settings.DEVELOPMENT
elif "localhost" in settings.DATABASE_URL or "mongodb:" in settings.DATABASE_URL:
    mongo_args["tls"] = False
else:
    mongo_args["tls"] = True
    mongo_args["tlsAllowInvalidCertificates"] = settings.DEVELOPMENT

client = pymongo.MongoClient(**mongo_args)

db = client.get_database("cineai")

chats = db["chats"]
projects = db["projects"]
users = db["users"]
analytics = db["analytics"]
