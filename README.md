Notification Service:-
A full-stack notification system built with Flask (backend) and a simple HTML/JavaScript (frontend) interface. It allows users to send email, SMS, or in-app notifications to registered users by specifying the type, message, and optional subject.

Features:-
 Send notifications (Email, SMS, In-App)
 View all notifications by user ID
 REST API with JSON support
 Simple and modern Bootstrap-based frontend (notification_ui.html)
 Error handling for failed API calls

 Tech Stack:-
Backend: Python Flask (app.py)
Frontend: HTML5 + Bootstrap 5 (notification_ui.html)
API Format: REST with JSON
Hosting: Deployable on platforms like Render

File Structure:-
notificationservice/

 app.py                  # Flask backend
 /templates/notification_ui.html    # Frontend UI
 requirements.txt        # Python dependencies

Setup Instructions:-
Prerequisites
Python 3.7+
pip package installer

Installation Steps:-
Clone the repository
Install dependencies
Run the Flask app

Deployment (Render.com):-
Deploying the Backend on Render
Create a new Web Service on Render.
Connect my GitHub repo.
Set the build and start commands:
Build command: pip install -r requirements.txt
Start command: guicorn app.py
Once deployed, i noted the Render URL (https://notification-services-183t.onrender.com/).

Update Frontend to Use Render API:-
In notification_ui.html, update the API variable:

Assumptions Made:-
Notifications are stored in memory (no database is used yet).
Only a local Flask server or a hosted Render backend is expected.
API assumes valid input (basic validation done in UI).
Only one instance of the app is assumed running at a time (due to in-memory storage).

Link to the deployed application :- https://notificationservice-40w4.onrender.com
