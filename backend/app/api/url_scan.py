from fastapi import APIRouter
from datetime import datetime, timezone
from app.models.schemas import URLScanRequest
from app.ml.predictor import predict_url
from app.core.database import get_db
import httpx
from app.core.config import settings

router = APIRouter()


async def check_virustotal(url: str) -> dict | None:
    api_key = settings.VIRUSTOTAL_API_KEY
    if not api_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            import base64
            url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
            resp = await client.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                headers={"x-apikey": api_key}
            )
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                return {
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0),
                    "undetected": stats.get("undetected", 0),
                }
    except Exception:
        return None
    return None


@router.post("/")
async def scan_url(request: URLScanRequest):
    result = predict_url(request.url)
    vt = await check_virustotal(request.url)
    if vt:
        result["virustotal"] = vt

    doc = {
        "scan_type": "url",
        "url": request.url,
        "prediction": result["prediction"],
        "risk_level": result["risk_level"],
        "phishing_probability": result["phishing_probability"],
        "confidence": result["confidence"],
        "indicators": result["indicators"],
        "virustotal": result.get("virustotal"),
        "created_at": datetime.now(timezone.utc),
    }
    db = get_db()
    inserted = await db.scan_history.insert_one(doc)
    result["id"] = str(inserted.inserted_id)

    return result
