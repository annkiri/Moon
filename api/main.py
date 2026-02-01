"""
Moon AI - FastAPI Backend
API server with SSE streaming for the PWA frontend.
"""

import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from api.routes.chat import router as chat_router
from api.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    print("[API] Moon AI API starting...")
    # Initialize database
    from src.core.database import init_db
    init_db()
    print("[API] Database initialized")
    yield
    print("[API] Moon AI API shutting down...")


app = FastAPI(
    title="Moon AI API",
    description="API backend for Moon AI PWA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://192.168.1.2:5173",
        "http://192.168.1.2:5174",
        # Wildcard for development (remove in production)
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
