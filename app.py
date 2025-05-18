"""
Notification Service – Flask API (queue-based)
----------------------------------------------
• POST  /notifications              → enqueue a notification task
• GET   /users/<user_id>/notifications  → list in-memory notifications
"""
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# -------------------------------------------------------------------------------------------------
#  Celery broker / queue
# -------------------------------------------------------------------------------------------------
from celery_app import celery                    # celery_app.py creates the Celery instance
from tasks import send_notification              # our task with retry logic
# -------------------------------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)                                        # allow any origin (adjust for prod)

# --------------------------- simple in-memory store (for demo only) ------------------------------
notifications = []                               # replace with DB in production
VALID_TYPES   = {"email", "sms", "in-app"}
# -------------------------------------------------------------------------------------------------

@app.route("/")
def root():
    """Serve the front-end UI (notification_ui.html in templates/)."""
    return render_template("notification_ui.html")


# -------------------------------------------------------------------------------------------------
#  API: enqueue a notification
# -------------------------------------------------------------------------------------------------
@app.route("/notifications", methods=["POST"])
def enqueue_notification():
    """
    JSON body:
    {
      "user_id": "1",
      "type": "email" | "sms" | "in-app",
      "subject": "optional subject",
      "message": "hello!"
    }
    """
    data = request.get_json(force=True) or {}
    missing = [k for k in ("user_id", "type", "message") if not data.get(k)]
    if missing:
        return jsonify(error=f"Missing field(s): {', '.join(missing)}"), 400
    if data["type"] not in VALID_TYPES:
        return jsonify(error="Invalid notification type"), 400

    # store a lightweight record locally (demo only)
    record = {
        "id"           : len(notifications) + 1,
        "user_id"      : str(data["user_id"]),
        "type"         : data["type"],
        "subject"      : data.get("subject"),
        "message"      : data["message"],
        "status"       : "queued",
        "attempt_count": 0,
        "timestamp"    : datetime.utcnow().isoformat()
    }
    notifications.append(record)

    # fire-and-forget Celery task
    task = send_notification.delay(record)       # pass the whole record (or just its ID)

    return (
        jsonify(
            message  = "Notification queued",
            task_id  = task.id,
            record   = record
        ),
        202
    )


# -------------------------------------------------------------------------------------------------
#  API: list user notifications
# -------------------------------------------------------------------------------------------------
@app.route("/users/<user_id>/notifications", methods=["GET"])
def list_notifications(user_id):
    user_notifs = [n for n in notifications if n["user_id"] == str(user_id)]
    return jsonify(notifications=user_notifs)


# -------------------------------------------------------------------------------------------------
#  Development entry-point
#  (Render/Gunicorn will ignore this and use its own start command)
# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

