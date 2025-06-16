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
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")

    firebase_cred_dict = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": private_key,
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
    }

    cred = credentials.Certificate(firebase_cred_dict)
    # Initialize the Firebase app with the loaded credentials
    firebase_admin.initialize_app(cred)
