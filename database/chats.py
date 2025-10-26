from database.database import chats
import uuid

# Estrutura de um chat:
# {
#   "_id": "chat_id_A",
#   "projectId": "project_id_123", 
#   "titulo": "Chat sobre Roteiro",
#   "descrição": "Brainstorm para o filme...",
#   "mensagens": [
#     { "role": "user", "content": "Me dê ideias...", "reasoning": null },
#     { "role": "assistant", "content": "...", "reasoning": "..." }
#   ]
# }

# Importe ObjectId para converter strings de ID em ObjectIds do MongoDB
from bson.objectid import ObjectId
# Assumindo que 'chats' é sua coleção do pymongo
# import pymongo
# client = pymongo.MongoClient("mongodb://...")
# db = client["your_db"]
# chats = db["your_collection"]

def createChat(title, description):
    chat_document = {
        "title": title, 
        "description": description, 
        "messages": []
    }
    chats.insert_one(chat_document)
    chat_document["_id"] = str(chat_document["_id"])
    
    return chat_document

def deleteChat(id):
    resultado = chats.delete_one({"_id": ObjectId(id)})
    return resultado.deleted_count > 0

def getChatHistory(id):
    queryResult = chats.find_one(
        {"_id": ObjectId(id)}, 
        {"_id": 0, "messages": 1}
    )
    return queryResult

def getChat(id):
    queryResult = chats.find_one(
        {"_id": ObjectId(id)}, 
        {"_id": 0, "title": 1, "description": 1, "messages": 1}
    )
    return queryResult

def getAllChatsDescriptions():
    queryResult = chats.find({}, {"title": 1, "description": 1})
    
    chat_list = []
    for doc in queryResult:
        doc["id"] = str(doc.pop("_id"))
        chat_list.append(doc)
        
    return chat_list

def addMessage(id, message):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$push": {"messages": message}}
    )

def removeLastMessage(id):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$pop": {"messages": 1}}
    )

def updateChatTitle(id, title):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$set": {"title": title}}
    )