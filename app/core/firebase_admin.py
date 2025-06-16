# Import necessary modules
# Firebase Admin SDK for server-side Firebase operations
# OS and JSON modules for environment variable handling
import firebase_admin
from firebase_admin import credentials
import os
import json
import base64

# Check if any Firebase app instances are already initialized
if not firebase_admin._apps:
    # Load Firebase credentials from environment variable
    encoded: str = os.getenv("FIREBASE_ADMIN_CREDENTIALS_BASE64") or ""
    decoded = base64.b64decode(encoded).decode("utf-8")
    cred = credentials.Certificate(json.loads(decoded))
    # Initialize the Firebase app with the loaded credentials
    firebase_admin.initialize_app(cred)
