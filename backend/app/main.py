from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import url_scan, email_scan, history, stats
from app.core.database import connect_db, close_db
from app.ml.trainer import ensure_model_trained

app = FastAPI(
    title="PhishGuard AI API",
    description="Real-Time AI/ML-Based Phishing Detection and Prevention System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()
    ensure_model_trained()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

app.include_router(url_scan.router, prefix="/api/v1/scan/url", tags=["URL Scan"])
app.include_router(email_scan.router, prefix="/api/v1/scan/email", tags=["Email Scan"])
app.include_router(history.router, prefix="/api/v1/history", tags=["History"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Stats"])

@app.get("/")
async def root():
    return {"message": "PhishGuard AI is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
