from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import uuid
import random
import time

app = Flask(__name__)
CORS(app)

# In-memory storage
notifications = []

VALID_TYPES = {"email", "sms", "in-app"}
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

@app.route("/")
def home():
    return render_template("notification_ui.html")

@app.route("/notifications", methods=["POST"])
def create_notification():
    data = request.get_json(force=True)
    user_id   = data.get("user_id")
    notif_type = data.get("type")
    message   = data.get("message")
    subject   = data.get("subject", "")

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

@app.route("/users/<user_id>/notifications", methods=["GET"])
def list_notifications(user_id):
    user_notifs = [n for n in notifications if n["user_id"] == str(user_id)]
    return jsonify(notifications=user_notifs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
