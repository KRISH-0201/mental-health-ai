from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import engine
from database.models import Base
from core.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from routes.chat_routes import router
from routes.analytics_routes import router as analytics_router
from routes.auth_routes import router as auth_router

app = FastAPI(
    title="Mental Health Companion API",
    description="AI-powered emotional support chatbot",
    version="1.0"
)

# ── Rate limiter ────────────────────────────────────────────
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# ── CORS — allow Streamlit frontend (and any origin in dev) ─
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create DB tables ────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Include routers ─────────────────────────────────────────
app.include_router(router)
app.include_router(analytics_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Mental Health Companion API is running"}
