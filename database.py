import os
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

# Connect to MongoDB Cloud Atlas Cluster
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

# 🌟 ADAPTIVE FALLBACK ENGINE: FIXES ATTRIBUTE ERRORS PERMANENTLY 🌟
def save_user(*args, **kwargs):
    """
    Adaptive fallback function that main.py expects during the Google OAuth callback.
    Intelligently auto-detects emails, phone numbers, and sheet IDs from incoming parameters.
    """
    email = kwargs.get("email")
    phone = kwargs.get("phone") or kwargs.get("phone_number")
    sheet_id = kwargs.get("sheet_id")
    
    # Intelligently inspect and parse whatever positional arguments main.py sends
    for arg in args:
        arg_str = str(arg).strip()
        if "@" in arg_str:
            email = arg_str
        elif arg_str.startswith("whatsapp:") or (arg_str.startswith("+") and arg_str[1:].isdigit()) or (arg_str.isdigit() and len(arg_str) >= 10):
            phone = arg_str
        elif len(arg_str) > 20:  # Google Sheet ID hashes are uniquely long strings (typically 44 chars)
            sheet_id = arg_str

    if phone and not str(phone).startswith("whatsapp:"):
        phone = f"whatsapp:{phone}"

    try:
        update_fields = {}
        if sheet_id: update_fields["sheet_id"] = sheet_id
        if email: update_fields["email"] = email
        if phone: update_fields["phone"] = phone

        if not update_fields:
            logger.warning("save_user triggered but no matching data archetypes identified.")
            return False

        # Query using whatever primary unique key is available (phone -> email -> sheet_id)
        query = {}
        if phone:
            query["phone"] = phone
        elif email:
            query["email"] = email
        else:
            query["sheet_id"] = sheet_id

        users_collection.update_one(query, {"$set": update_fields}, upsert=True)
        logger.info(f"💾 Dynamic Session Saved to Cluster: {update_fields}")
        return True
    except Exception as e:
        logger.error(f"MongoDB save_user handling failure: {e}")
        return False