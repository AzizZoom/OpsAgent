import os
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

# Connect to MongoDB Cloud
MONGO_URI = os.getenv("MONGO_URI") 
client = MongoClient(MONGO_URI)
db = client["OpsAgentDB"]
users_collection = db["users"]

def get_user_by_phone(phone_number):
    try:
        user = users_collection.find_one({"phone": phone_number})
        return user
    except Exception as e:
        logger.error(f"MongoDB Read Error: {e}")
        return None

def save_user_session(phone_number, sheet_id, email=None):
    try:
        users_collection.update_one(
            {"phone": phone_number},
            {"$set": {"phone": phone_number, "sheet_id": sheet_id, "email": email}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"MongoDB Write Error: {e}")
        return False