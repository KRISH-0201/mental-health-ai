from fastapi import FastAPI, Request
from database.db import engine
from database.models import Base
from core.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(
    title="Mental Health Companion API",
    description="AI-powered emotional support chatbot",
    version="1.0"
)

# Rate limiter — set ONCE, before middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Mental Health Companion API is running"}

from routes.chat_routes import router
from routes.analytics_routes import router as analytics_router
from routes.auth_routes import router as auth_router

app.include_router(router)
app.include_router(analytics_router)
app.include_router(auth_router)

