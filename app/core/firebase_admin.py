import firebase_admin
from firebase_admin import credentials
import os
import json

if not firebase_admin._apps:
    cred = credentials.Certificate(
        json.loads(os.getenv("FIREBASE_ADMIN_CREDENTIALS") or "")
    )
    firebase_admin.initialize_app(cred)
