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

# 1. Define specific origins for better compatibility
origins = [
    "https://website-qa-engine.vercel.app",
    "http://localhost:3000",
]

# 2. Add middleware explicitly
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 3. Include routers AFTER middleware setup
app.include_router(analyze_router)
app.include_router(ask_router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "website-qa-engine",
    }
