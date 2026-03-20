import pymongo
from src.core.config import settings

client = pymongo.MongoClient(
    host=settings.DATABASE_URL.split(","),
    tls=True,
    tlsAllowInvalidCertificates=settings.DEVELOPMENT,
    retryWrites=False,
)

db = client.get_database("cineai")

# Collections
chats = db["chats"]
projects = db["projects"]
users = db["users"]
