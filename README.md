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

## 💻 Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/lifedrop.git
   cd lifedrop
   ```

2. **Run locally with Python**:
   ```bash
   python -m http.server 8080
   ```

3. Open **`http://localhost:8080`** in your browser.

---

## 📁 Project Structure

```text
lifedrop/
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
│   ├── app.js            # Core App Orchestration & Interactivity
│   ├── data.js           # Blood Group Data & Initial Registry
│   ├── storage.js        # Local Persistence & State Manager
│   ├── assistant.js      # Lifedrop AI Assistant Bot Logic
│   └── tracker.js        # Dispatch Pipeline & Status Engine
└── assets/               # Logos, Icons & Vector Graphics
```

---

## 📄 License
MIT License. Built to support emergency healthcare coordination.
