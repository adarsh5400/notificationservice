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
CORS(app)                       # allow requests from the HTML file

# In-memory storage
notifications = []              # list of dicts – each is a notification

# Accepted notification types
VALID_TYPES = {"email", "sms", "in-app"}

# ---------------------------------------------------------------------
# Helper: simulate sending (with optional random failure + retry)
# ---------------------------------------------------------------------
MAX_ATTEMPTS = 3

def send_with_retry(notification):
    """Simulate delivery, retrying if we randomly 'fail'."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        success = random.random() > 0.2          # 80 % chance of success
        if success:
            notification["status"] = "sent"
            notification["attempt_count"] = attempt
            break
        notification["status"] = "failed"
        notification["attempt_count"] = attempt
        time.sleep(0.5)                          # small delay before retry
    return notification["status"]

# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------
@app.route("/notifications", methods=["POST"])
def create_notification():
    data = request.get_json(force=True)
    user_id   = data.get("user_id")
    notif_type = data.get("type")
    message   = data.get("message")
    subject   = data.get("subject", "")          # email only – optional

    # Basic validation -------------------------------------------------
    if not user_id or not notif_type or not message:
        return jsonify(error="Missing user_id, type, or message"), 400
    if notif_type not in VALID_TYPES:
        return jsonify(error="Invalid notification type"), 400

    # Build notification object ---------------------------------------
    notification = {
        "id"           : str(uuid.uuid4()),
        "user_id"      : str(user_id),
        "type"         : notif_type,
        "subject"      : subject,
        "message"      : message,
        "status"       : "queued",
        "attempt_count": 0,
        "timestamp"    : datetime.utcnow().isoformat()
    }

    # Simulate sending -------------------------------------------------
    send_with_retry(notification)

    # Store after attempts complete
    notifications.append(notification)

    return (
        jsonify(
            message="Notification processed",
            data=notification
        ),
        201
    )

@app.route("/users/<user_id>/notifications", methods=["GET"])
def list_notifications(user_id):
    user_notifs = [n for n in notifications if n["user_id"] == str(user_id)]
    return jsonify(notifications=user_notifs)

# ---------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
