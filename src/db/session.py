import pymongo
from src.core.config import settings

# Handle different connection string formats
is_cloud = "mongodb+srv" in settings.DATABASE_URL or "ssl=true" in settings.DATABASE_URL.lower()

mongo_args = {
    "host": settings.DATABASE_URL,
    "retryWrites": False,
}

# If it's a comma separated list (CosmoDB style)
if "," in settings.DATABASE_URL:
    mongo_args["host"] = settings.DATABASE_URL.split(",")

# Configure TLS based on environment and URL type
if is_cloud:
    mongo_args["tls"] = True
    mongo_args["tlsAllowInvalidCertificates"] = settings.DEVELOPMENT
elif "localhost" in settings.DATABASE_URL or "mongodb:" in settings.DATABASE_URL:
    # Local/Docker usually doesn't use TLS
    mongo_args["tls"] = False
else:
    # Default to secure if not explicitly local
    mongo_args["tls"] = True
    mongo_args["tlsAllowInvalidCertificates"] = settings.DEVELOPMENT

client = pymongo.MongoClient(**mongo_args)

db = client.get_database("cineai")

# Collections
chats = db["chats"]
projects = db["projects"]
users = db["users"]
analytics = db["analytics"]
