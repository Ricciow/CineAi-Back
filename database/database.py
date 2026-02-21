import pymongo

DATABASE_URL = "mongodb://mongodb:27017"

client = pymongo.MongoClient(DATABASE_URL)

print("Conectando com MongoDB...")
print("Conectado com MongoDB")

db = client.get_database("cineai")

chats = db["chats"]
projects = db["projects"]
users = db["users"]

