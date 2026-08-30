import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analyze import router as analyze_router
from app.api.ask import router as ask_router

app = FastAPI(
    title="Website QA Engine",
    description="A retrieval-based question answering system",
    version="0.1.0",
)

# Get frontend URL from env and strip trailing slash if present
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://website-qa-engine.vercel.app",  # Hardcoded production fallback
    frontend_url,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(ask_router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "website-qa-engine",
    }