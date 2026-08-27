# 🩸 Lifedrop — Rapid Blood Donor Network & Emergency Assistant

Lifedrop is an emergency blood donor matching platform and AI assistant designed to connect patients in urgent need of blood with compatible, verified donors in minutes.

---

## 🌟 Key Features

- **⚡ Instant Donor Matching & Search**: Filter donors by blood type, location, urgency, and live availability.
- **🧬 Interactive Blood Compatibility Matrix**: Visual guidelines showing donor and recipient compatibility across all ABO and Rh blood groups.
- **🚨 Emergency Blood Request Flow**: Instant emergency broadcast forms with automated priority flags.
- **📍 Live Request Tracker**: Real-time status tracking for hospital dispatches and donor confirmations.
- **🤖 Lifedrop AI Assistant**: Built-in chatbot for rapid triage, blood request routing, donor registration, and status lookups.
- **📱 Clean & Responsive UI**: Built with modern aesthetics, dark/light theme support, and fluid layout.

---

## 🚀 Live Demo / GitHub Pages

Once published, you can access the live application directly via GitHub Pages:
`https://<your-username>.github.io/<repository-name>/`

---

## 💻 Full-Stack Local Setup & Backend

### 1. Start the Python + Flask Backend Server & Database
```bash
# Start backend server & SQLite database (serves REST API & static frontend)
python backend/server.py
```
> Server runs on **`http://127.0.0.1:5000`** with live database `lifedrop.db`.

### 2. Optional: Reset / Re-seed Database
```bash
python backend/seed.py
```

### 3. Run Backend Test Suite
```bash
python -m unittest tests/test_backend.py
```

---

## 🗄️ Database & REST API Architecture

* **Database**: Embedded relational **SQLite3** (`lifedrop.db`)
* **Backend Framework**: Python 3 + Flask + Flask-CORS
* **Key API Endpoints**:
  * `GET /api/health` - Backend status and health
  * `GET /api/stats` - Live donor metrics, active requests, lives saved
  * `GET /api/donors` - Filter donors by blood type, city, availability
  * `POST /api/donors` - Register new verified donor
  * `GET /api/donors/match?bloodGroup=...&city=...` - Real-time compatible donor search
  * `GET /api/requests` - Active emergency blood requests feed
  * `POST /api/requests` - Submit urgent request + trigger automated donor alerts
  * `GET /api/requests/<id>` - Live request tracker with dispatch timeline
  * `GET /api/inventory` - Blood bank inventory stock levels

---

## 📁 Project Structure

```text
lifedrop/
├── lifedrop.db           # SQLite Relational Database
├── backend/
│   ├── db.py             # Schema initialization & connection factory
│   ├── models.py         # Business logic, SQL queries & compatibility engine
│   ├── server.py         # Flask REST API & static file host
│   └── seed.py           # Database seeder utility
├── tests/
│   └── test_backend.py   # Unit & Integration test suite
├── index.html            # Main Landing & Emergency Portal
├── dashboard.html        # Emergency Metrics & Case Overview
├── donors.html           # Verified Donor Directory & Filters
├── requests.html         # Emergency Request Submission & Feeds
├── tracker.html          # Live Dispatch Tracker
├── compatibility.html    # Blood Compatibility Matrix
├── register.html         # Donor Registration Form
├── css/
│   ├── style.css         # Main Design System & UI Styling
│   └── chat.css          # Assistant & Chatbot Interface
├── js/
│   ├── api.js            # REST API Client & Server Sync Layer
│   ├── app.js            # Core App Orchestration & Interactivity
│   ├── data.js           # Blood Group Data & Initial Registry
│   ├── storage.js        # Hybrid State Manager (SQLite + Offline Fallback)
│   ├── assistant.js      # Lifedrop AI Assistant Bot Logic
│   └── tracker.js        # Dispatch Pipeline & Status Engine
└── assets/               # Logos, Icons & Vector Graphics
```

---

## 📄 License
MIT License. Built to support emergency healthcare coordination.
