# Import necessary modules
# Motor for asynchronous MongoDB operations
# dotenv for loading environment variables
# os for accessing environment variables

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Get the MongoDB URL from environment variables or use a default
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)

# Get the MongoDB database name from environment variables or use a default
MONGO_DB = os.getenv("MONGO_DB", "mydatabase")
db = client[MONGO_DB]
