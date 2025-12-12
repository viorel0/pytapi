# Water Quality Monitoring API & Tester

A robust Flask-based REST API for tracking environmental water quality data (pH, turbidity, etc.). This project includes a custom **HTML/JavaScript frontend** that serves as a built-in API testing tool, allowing users to interact with the database without external tools like Postman.

## 🚀 Features

### Backend (API)
- **CRUD Operations:** Create, Read, Update, and Delete water quality measurements.
- **Bulk Operations:** Supports batch creation and batch updates for high-volume data.
- **Robust Error Handling:** Implements `try-except-finally` blocks to prevent database connection leaks.
- **Transaction Safety:** Automatic `rollback` on errors ensures data integrity during failed operations.
- **REST Standards:** Uses HTTP status codes (`200`, `201`, `400`, `404`, `500`).

### Frontend (UI)
- **Interactive Tester:** A built-in web interface to send GET, POST, PUT, and DELETE requests.
- **JSON Validation:** Client-side JavaScript validates JSON before sending it to the server.
- **Real-time Feedback:** Displays formatted JSON responses and HTTP status codes directly in the browser.

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Framework:** Flask
- **Database:** PostgreSQL
- **Driver:** Psycopg2 (Binary)
- **Frontend:** HTML, CSS, JavaScript

## 📂 Project Structure

```text
/project-root
├── api3.py               # Main Flask application
├── requirements.txt     # Python dependencies
├── Procfile             # For deployment (e.g., Heroku)
├── .env                 # Database credentials (not committed to git)
├── templates/
│   └── index.html       # The API Testing Interface
└── static/
    ├── style.css        # Styling for the interface
    └── script.js        # Logic for sending API requests
