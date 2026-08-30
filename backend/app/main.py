from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router
from app.api.ask import router as ask_router


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Website QA Engine",
    description=(
        "A retrieval-based question answering system "
        "that answers using website content only."
    ),
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

# Production frontend + local development origins.
ALLOWED_ORIGINS = [
    "https://website-qa-engine.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(analyze_router)
app.include_router(ask_router)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "website-qa-engine",
    }
