from agents import SQLiteSession
import asyncio
session = SQLiteSession("user_1234", "conversations.db")


def extract_text(item):
    content = item.get("content")
    if item["role"] == "user":
        return content
    elif item["status"] == "completed":
        return content[0]["text"]
    return None

async def main():
    items = await session.get_items()
    for item in items:
        text = extract_text(item)
        if text:
            print(text)

asyncio.run(main())