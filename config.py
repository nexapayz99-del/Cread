import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
MONGO_URI = os.getenv("MONGO_URI")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))

# Plan limits (per user)
PLANS = {
    "free":   {"reactions": 5,   "views": 10,  "vc_joins": 1,   "accounts": 0},
    "bronze": {"reactions": 50,  "views": 200, "vc_joins": 3,   "accounts": 5},
    "silver": {"reactions": 200, "views": 1000,"vc_joins": 7,   "accounts": 15},
    "gold":   {"reactions": 999, "views": 9999,"vc_joins": 15,  "accounts": 50},
    "owner":  {"reactions": 99999,"views": 99999,"vc_joins": 100,"accounts": 1000},
}
