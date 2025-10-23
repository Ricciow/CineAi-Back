import pymongo

from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "").split(",")
DEVELOPMENT = os.environ.get("DEVELOPMENT", "false")
if(DEVELOPMENT == "true"):
    DEVELOPMENT = True
else:
    DEVELOPMENT = False

client = pymongo.MongoClient(
    host=DATABASE_URL,
    tls=True,
    tlsAllowInvalidCertificates=DEVELOPMENT,
    retryWrites=False,
)

print("Conectando com CosmoDB...")
if(client.is_mongos):
    print("Conectado com CosmoDB")

db = client.get_database("cineai")

chats = db["chats"]
users = db["users"]

