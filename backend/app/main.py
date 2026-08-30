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

# Senior Dev Fix: Wildcard CORS configuration to unblock preflight completely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
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