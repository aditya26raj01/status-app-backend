from fastapi import WebSocket
import json

# List to store active WebSocket connections
active_connections = []


async def broadcast_message(message: dict):
    # Serialize the message to a JSON string
    message_json = json.dumps(message)
    for connection in active_connections:
        await connection.send_text(message_json)
