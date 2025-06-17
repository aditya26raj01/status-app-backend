# Import necessary modules
# Firebase Admin SDK for server-side Firebase operations
# OS and JSON modules for environment variable handling
import firebase_admin
from firebase_admin import credentials
import os
import json
from dotenv import load_dotenv

load_dotenv()

firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

# Check if any Firebase app instances are already initialized
if not firebase_admin._apps:
    # Load Firebase credentials from environment variable
    cred = credentials.Certificate(json.loads(firebase_json or ""))
    # Initialize the Firebase app with the loaded credentials
    firebase_admin.initialize_app(cred)
