# 🛡️ PhishGuard AI — Real-Time Phishing Detection & Prevention System

> Final Year Project — ML-Based Cybersecurity System  
> **Stack:** React · FastAPI · scikit-learn · MongoDB

---

## 📁 Project Structure

```
phishing-detection/
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # App entry point
│   │   ├── api/              # Route handlers
│   │   │   ├── url_scan.py   # URL scan endpoint
│   │   │   ├── email_scan.py # Email scan endpoint
│   │   │   ├── history.py    # Scan history CRUD
│   │   │   └── stats.py      # Dashboard statistics
│   │   ├── ml/               # ML engine
│   │   │   ├── feature_extractor.py  # 25+ URL features
│   │   │   ├── trainer.py            # Model training (RF)
│   │   │   └── predictor.py          # Prediction logic
│   │   ├── models/
│   │   │   └── schemas.py    # Pydantic data models
│   │   └── core/
│   │       ├── config.py     # Environment settings
│   │       └── database.py   # MongoDB connection
│   ├── requirements.txt
│   └── .env
│
└── frontend/                 # React + Vite frontend
    ├── src/
    │   ├── App.jsx
    │   ├── pages/
    │   │   ├── DashboardPage.jsx
    │   │   ├── URLScanPage.jsx
    │   │   ├── EmailScanPage.jsx
    │   │   └── HistoryPage.jsx
    │   ├── components/
    │   │   ├── layout/Layout.jsx
    │   │   └── ui/           # Reusable components
    │   └── services/api.js   # Axios API layer
    ├── package.json
    └── vite.config.js
```

---

## ⚙️ Prerequisites

Ensure the following are installed on your machine:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| MongoDB | 6+ (Community) | https://mongodb.com/try/download/community |
| VS Code | Latest | https://code.visualstudio.com |

---

## 🚀 Setup & Installation

### 1. Clone / Extract the project

```bash
cd phishing-detection
```

### 2. Start MongoDB

**Windows:**
```bash
mongod --dbpath C:\data\db
```
**macOS/Linux:**
```bash
mongod --dbpath ~/data/db
# or if installed as service:
sudo systemctl start mongod
```

---

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Add VirusTotal API key to .env
# Get a free key at https://www.virustotal.com/gui/my-apikey
# Edit .env → VIRUSTOTAL_API_KEY=your_key_here

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The ML model will be **automatically trained** on first startup.  
API documentation available at: **http://localhost:8000/docs**

---

### 4. Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend available at: **http://localhost:5173**

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/scan/url/` | Scan a URL for phishing |
| `POST` | `/api/v1/scan/email/` | Scan email content |
| `GET` | `/api/v1/history/` | Retrieve scan history |
| `DELETE` | `/api/v1/history/{id}` | Delete a history entry |
| `GET` | `/api/v1/stats/` | Get dashboard statistics |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

### Example — Scan a URL

```bash
curl -X POST http://localhost:8000/api/v1/scan/url/ \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-secure-login.xyz/verify"}'
```

### Example — Scan an Email

```bash
curl -X POST http://localhost:8000/api/v1/scan/email/ \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent: Verify your account",
    "body": "Click here: http://phish.tk/login to verify",
    "sender": "support@paypal-verify.ml"
  }'
```

---

## 🤖 ML Model Details

| Property | Value |
|----------|-------|
| Algorithm | Random Forest Classifier |
| Library | scikit-learn |
| Features | 25+ extracted URL features |
| Training | Auto-trains on startup if model not found |
| Model file | `backend/app/ml/models/phishing_model.pkl` |

### Features Extracted

- **Length-based:** URL length, hostname length, path length
- **Structural:** dots, hyphens, @ symbols, subdomains, query params
- **Security:** HTTPS usage, port detection, IP-in-URL
- **TLD analysis:** suspicious vs trusted top-level domains
- **Keyword matching:** 25+ phishing keyword patterns
- **Entropy:** hostname randomness score (Shannon entropy)
- **Obfuscation:** URL encoding, double slashes, redirect chains
- **Shorteners:** bit.ly, tinyurl, goo.gl detection

---

## 🔑 Optional: VirusTotal Integration

1. Create a free account at https://www.virustotal.com
2. Get your API key from your profile
3. Edit `backend/.env`:
   ```
   VIRUSTOTAL_API_KEY=your_api_key_here
   ```
4. URL scans will now include VirusTotal engine results

---

## 🛠️ VS Code Tips

Install these recommended extensions:
- **Python** (Microsoft)
- **Pylance**
- **ES7+ React/Redux/React-Native snippets**
- **Prettier**
- **MongoDB for VS Code**

Open the project as two separate VS Code windows or use the split terminal feature to run both servers simultaneously.

---

## 🗄️ Database

- **Engine:** MongoDB (local)
- **Database name:** `phishguard`
- **Collection:** `scan_history`

Each scan document contains: scan type, input data, prediction, risk level, indicators, timestamps.

---

## 📦 Retrain the Model

To retrain with fresh data:

```bash
cd backend
python -c "from app.ml.trainer import train_model; train_model()"
```

To use a real dataset (recommended for production), download the PhishTank dataset and replace the URL lists in `app/ml/trainer.py`.

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Ensure virtualenv is active before running uvicorn |
| `Connection refused` | Make sure MongoDB is running on port 27017 |
| `CORS error` | Backend must be on port 8000, frontend on 5173 |
| `Model not found` | Delete `.pkl` file and restart; it will retrain |
| Frontend blank page | Check browser console; confirm backend is running |

---

## 👨‍💻 Author

**Final Year Student**  
Department of Computer Science & Engineering  
Real-Time AI/ML-Based Phishing Detection and Prevention System
