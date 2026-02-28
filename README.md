# 🧠 Mental Health AI Chatbot

> **Solace** — Your private AI-powered mental health companion. A safe space to feel, reflect, and grow.

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/ML-PyTorch-EE4C2C?style=flat-square&logo=pytorch)](https://pytorch.org/)
[![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=flat-square)](https://groq.com/)

---

## 📖 Overview

**Mental Health AI Chatbot** is a full-stack AI application that provides empathetic, context-aware emotional support. It uses a transformer-based emotion detection model combined with Groq's LLM to generate warm, personalized responses. The app tracks your emotional journey over time and provides insights through a beautiful analytics dashboard.

### Key Highlights

- 🤖 **AI Companion "Solace"** — Context-aware, empathetic conversation powered by Groq LLM
- 🎭 **Real-time Emotion Detection** — Transformer model classifies emotions from your messages
- 🔥 **Burnout Score Tracker** — Dynamic score adjusted by emotional patterns over time
- 📊 **Weekly Wellness Dashboard** — Visualize your emotional trends with interactive charts
- 📓 **Journal Mode** — Save private thoughts with `/journal` prefix
- 🚨 **Crisis Detection** — Automatically provides helpline resources for at-risk messages
- 🌗 **Light / Dark Theme** — Glassmorphism UI with smooth animations
- 🔐 **JWT Authentication** — Secure login/signup with access & refresh tokens

---

## 🏗️ Architecture

```
mental-health-ai/
├── backend/                    # FastAPI REST API
│   ├── main.py                 # App entrypoint, middleware, routers
│   ├── routes/
│   │   ├── auth_routes.py      # /signup, /login, /refresh
│   │   ├── chat_routes.py      # /chat — core chat + emotion pipeline
│   │   └── analytics_routes.py # /weekly-wellness, /emotion-history
│   ├── services/
│   │   ├── emotion_service.py  # HuggingFace transformer inference
│   │   ├── llm_service.py      # Groq API calls
│   │   ├── risk_service.py     # Crisis keyword detection
│   │   ├── burnout_service.py  # Burnout score logic
│   │   ├── mental_state_analyzer.py
│   │   ├── emotion_interpreter.py
│   │   └── analytics_service.py
│   ├── database/
│   │   ├── db.py               # SQLAlchemy engine & session
│   │   └── models.py           # ORM models (ChatHistory, EmotionLog, etc.)
│   ├── schemas/
│   │   └── request_models.py   # Pydantic schemas
│   ├── core/
│   │   ├── security.py         # JWT token handling
│   │   └── rate_limiter.py     # SlowAPI rate limiting
│   └── requirements.txt
│
├── frontend/                   # Streamlit UI
│   ├── app.py                  # Full single-page app
│   └── requirements.txt
│
├── ml_models/                  # Local model weights (not tracked in Git)
├── training/                   # Model training scripts
└── requirements.txt            # Combined deps (optional)
```

---

## ✨ Features

### 💬 Chat Pipeline
1. User sends a message
2. Emotion detected via transformer model (e.g., `sadness`, `joy`, `anxiety`)
3. Burnout score is updated based on emotion weights
4. System prompt is enriched with emotion context & burnout level
5. Groq LLM generates a warm, personalized response
6. Chat history (last 6 messages) provides conversation memory

### 📊 Analytics Dashboard
- **Weekly Wellness Chart** — Spline area chart of daily average emotional intensity
- **Burnout Gauge** — Color-coded gauge (green → yellow → red) from 0–100
- **Emotion Sidebar** — Live dominant emotion with progress bar
- **Day Streak** — Tracks consecutive days of engagement

### 📓 Journal Mode
Prefix any message with `/journal` to save it as a private journal entry without triggering AI response.

### 🚨 Crisis Response
Detects keywords like `suicide`, `want to die`, `hurt myself` and immediately responds with Indian helpline numbers:
- 📞 **iCALL**: 9152987821
- 📞 **KIRAN**: 1800-599-0019 (Free, 24/7)
- 📞 **AASRA**: +91-22-27546669

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A [Groq API key](https://console.groq.com/) (free tier available)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/mental-health-ai.git
cd mental-health-ai
```

### 2. Set Up the Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example env file
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Edit `.env` and fill in your values:

```env
SECRET_KEY=your_super_secure_random_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Start the Backend

```bash
# From the /backend directory
uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

### 5. Set Up the Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🔌 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/signup` | ❌ | Register a new user |
| `POST` | `/login` | ❌ | Login & receive JWT tokens |
| `POST` | `/chat` | ✅ | Send message, get AI response + emotion data |
| `GET` | `/weekly-wellness` | ✅ | Get last 7 days of wellness data |
| `GET` | `/emotion-history` | ✅ | Get recent emotion logs |

**Chat Response Example:**
```json
{
  "emotion": "anxiety",
  "emotion_score": 87,
  "burnout_score": 42,
  "streak": 5,
  "response": "Hey Krish, I hear you — anxiety can feel really overwhelming..."
}
```

---

## 🔒 Security

- Passwords are hashed with **bcrypt** via `passlib`
- Authentication uses **JWT** (access + refresh tokens) via `python-jose`
- Rate limiting via **SlowAPI** to prevent abuse
- CORS configured (tighten `allow_origins` in production)
- `.env` file keeps secrets out of version control

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit, Plotly |
| Database | SQLite + SQLAlchemy |
| ML Model | PyTorch, HuggingFace Transformers |
| LLM | Groq (Llama / Mixtral) |
| Auth | JWT (python-jose), bcrypt |
| Rate Limiting | SlowAPI |

---

## 🌐 Deployment

The backend is configured for **Railway** deployment:

- `Procfile` — Defines the web process
- `railway.json` — Railway configuration
- `nixpacks.toml` — Build config

Set the `BACKEND_URL` environment variable in your frontend deployment to point to your Railway backend URL.

---

## ⚠️ Disclaimer

This application is **not** a substitute for professional mental health care. If you are in crisis, please contact a licensed mental health professional or a crisis hotline immediately.

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute it with attribution.
