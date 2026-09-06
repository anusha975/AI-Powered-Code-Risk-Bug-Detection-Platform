# Installation & Deployment Guide

## 1. System Requirements

- **Python**: Version 3.10 or higher (Python 3.11/3.12/3.13 supported).
- **Node.js**: Version 18.0 or higher with `npm`.
- **Operating System**: Linux, macOS, or Windows 10/11.
- **Database (Optional)**: PostgreSQL 14+ (Platform operates fully in-memory if database is offline).
- **Local LLM Server (Optional)**: Ollama (e.g. `ollama run llama3.2:1b`) or vLLM on local network.

---

## 2. Quickstart Installation

### Step 1: Clone Repository & Setup Environment
```bash
git clone https://github.com/anusha975/AI-Powered-Code-Risk-Bug-Detection-Platform.git
cd "Privacy-Preserving AI Code Security"
```

### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 3. Running Locally (Development Mode)

### Start Backend API Server
```bash
cd backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API**: `http://127.0.0.1:8000`
- **Swagger UI Docs**: `http://127.0.0.1:8000/docs`

### Start Frontend Console
```bash
cd frontend
npm run dev
```
- **Web Dashboard**: `http://127.0.0.1:5173`

---

## 4. Running the Test Suites

### Backend Unit & Integration Tests (135 tests)
```bash
cd backend
.venv\Scripts\pytest -v
```

### Frontend Production Bundle Build
```bash
cd frontend
npm run build
```

---

## 5. Production Deployment (Single-Host / VM Architecture)

The application is structured as a streamlined **Modular Monolith**, allowing reliable single-server deployment without microservices complexity:

```
┌────────────────────────────────────────────────────────┐
│               HOST SERVER (Linux / Windows)             │
│                                                        │
│  [Nginx / Caddy Reverse Proxy] (TLS 1.3 Termination)  │
│         │                                              │
│         ├──→ Port 5173 / Static: Built Frontend Assets │
│         └──→ Port 8000: Uvicorn ASGI Backend Process   │
│                   │                                    │
│                   └──→ Local Ollama Server (Port 11434)│
└────────────────────────────────────────────────────────┘
```

### Systemd Service Configuration (Linux Example)
```ini
[Unit]
Description=Privacy-Preserving AI Code Security Backend
After=network.target

[Service]
User=securityapp
WorkingDirectory=/opt/code-security/backend
ExecStart=/opt/code-security/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```
