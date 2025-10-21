import pymongo

from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "").split(",")

client = pymongo.MongoClient(
    host=DATABASE_URL,
    tls=True,
    tlsAllowInvalidCertificates=True,
    retryWrites=False,
)

db = client["cineai"]
if "cineai" not in client.list_database_names():
    db.command(
        {
            "customAction": "CreateDatabase",
            "offerThroughput": 400,
        }
    )

if "chats" not in db.list_collection_names():
    db.command({"customAction": "CreateCollection", "collection": "chats"})

if "users" not in db.list_collection_names():
    db.command({"customAction": "CreateCollection", "collection": "users"})

chats = db["chats"]
users = db["users"]

