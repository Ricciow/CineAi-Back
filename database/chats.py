from database.database import chats
import uuid

def createChat(title, description):
    object = {
        "id": str(uuid.uuid4()),
        "title": title, 
        "description": description, 
        "messages": []
    }
    chats.insert_one(object)
    del object["_id"]
    return object


def deleteChat(id):
    resultado = chats.delete_one({"id": id})
    return resultado.deleted_count > 0

def getChatHistory(id):
    queryResult = chats.find_one({"id": id}, {"_id": 0, "messages": 1})
    return queryResult

def getChat(id):
    queryResult = chats.find_one({"id": id}, {"_id": 0, "title": 1, "description": 1, "messages": 1})
    return queryResult

def getAllChatsDescriptions():
    queryResult = chats.find({}, {"_id": 0, "title": 1, "description": 1, "id": 1})
    return list(queryResult)

def addMessage(id, message):
    chats.update_one({"id": id}, {"$push": {"messages": message}})

def removeLastMessage(id):
    chats.update_one({"id": id}, {"$pop": {"messages": 1}})

def updateChatTitle(id, title):
    chats.update_one({"id": id}, {"$set": {"title": title}})