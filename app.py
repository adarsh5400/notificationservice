"""
Notification Service – minimal Flask backend
--------------------------------------------
Runs on http://127.0.0.1:5000
Endpoints:
  POST /notifications               – send (store) a notification
  GET  /users/<user_id>/notifications – list notifications for a user
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import random
import time

app = Flask(__name__)
CORS(app)

# ✅ Root route
@app.route('/')
def home():
    return "Server is running!"

# In-memory storage
notifications = []

# Accepted notification types
VALID_TYPES = {"email", "sms", "in-app"}

# Helper: simulate sending with retry
MAX_ATTEMPTS = 3

def send_with_retry(notification):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        success = random.random() > 0.2
        if success:
            notification["status"] = "sent"
            notification["attempt_count"] = attempt
            break
        notification["status"] = "failed"
        notification["attempt_count"] = attempt
        time.sleep(0.5)
    return notification["status"]

# POST /notifications
@app.route("/notifications", methods=["POST"])
def create_notification():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    notif_type = data.get("type")
    message = data.get("message")
    subject = data.get("subject", "")

    if not user_id or not notif_type or not message:
        return jsonify(error="Missing user_id, type, or message"), 400
    if notif_type not in VALID_TYPES:
        return jsonify(error="Invalid notification type"), 400

    notification = {
        "id": str(uuid.uuid4()),
        "user_id": str(user_id),
        "type": notif_type,
        "subject": subject,
        "message": message,
        "status": "queued",
        "attempt_count": 0,
        "timestamp": datetime.utcnow().isoformat()
    }

    send_with_retry(notification)
    notifications.append(notification)

    return jsonify(message="Notification processed", data=notification), 201

# GET /users/<user_id>/notifications
@app.route("/users/<user_id>/notifications", methods=["GET"])
def list_notifications(user_id):
    user_notifs = [n for n in notifications if n["user_id"] == str(user_id)]
    return jsonify(notifications=user_notifs)

# Run server locally
if __name__ == "__main__":
    app.run(debug=True)
