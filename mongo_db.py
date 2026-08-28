import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# We expect MONGODB_URI in the environment. For local testing without a DB, 
# we can gracefully fail or provide a mock if it's strictly required later.
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(MONGO_URI)
            cls.db = cls.client.agentic_commerce
            print(f"Connected to MongoDB at {MONGO_URI}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")

    @classmethod
    def disconnect(cls):
        if cls.client:
            cls.client.close()
            print("Disconnected from MongoDB")

    @classmethod
    def get_collection(cls, collection_name: str):
        if cls.db is None:
            cls.connect()
        return cls.db[collection_name]

# Helper functions for the Buyer Agent

async def save_session_message(session_id: str, message: dict):
    collection = MongoDB.get_collection("sessions")
    await collection.update_one(
        {"session_id": session_id},
        {"$push": {"messages": message}},
        upsert=True
    )

async def get_session_history(session_id: str):
    collection = MongoDB.get_collection("sessions")
    doc = await collection.find_one({"session_id": session_id})
    if doc:
        return doc.get("messages", [])
    return []

async def update_customer_profile(customer_id: str, summary: str):
    collection = MongoDB.get_collection("profiles")
    await collection.update_one(
        {"customer_id": customer_id},
        {"$set": {"memory_summary": summary}},
        upsert=True
    )

async def get_customer_profile(customer_id: str):
    collection = MongoDB.get_collection("profiles")
    doc = await collection.find_one({"customer_id": customer_id})
    if doc:
        return doc.get("memory_summary", "")
    return ""

async def create_transaction(transaction_data: dict):
    collection = MongoDB.get_collection("transactions")
    result = await collection.insert_one(transaction_data)
    return str(result.inserted_id)

async def update_transaction_status(transaction_id: str, status: str):
    from bson.objectid import ObjectId
    collection = MongoDB.get_collection("transactions")
    await collection.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"status": status}}
    )
