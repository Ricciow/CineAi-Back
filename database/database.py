import pymongo

from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "").split(",")

client = pymongo.MongoClient(
    host=DATABASE_URL,
    tls=True,
    # tlsAllowInvalidCertificates=True,
    retryWrites=False,
)

print("Conectado com cosmoDB")

db = client.get_database("cineai")

if "chats" not in db.list_collection_names():
    db.create_collection("chats")

if "users" not in db.list_collection_names():
    db.create_collection("users")

chats = db["chats"]
users = db["users"]

