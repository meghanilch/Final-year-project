from fastapi import APIRouter
from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def get_stats():
    db = get_db()
    total = await db.scan_history.count_documents({})
    phishing = await db.scan_history.count_documents({"prediction": "phishing"})
    legitimate = await db.scan_history.count_documents({"prediction": "legitimate"})
    url_scans = await db.scan_history.count_documents({"scan_type": "url"})
    email_scans = await db.scan_history.count_documents({"scan_type": "email"})
    danger_count = await db.scan_history.count_documents({"risk_level": "danger"})
    warning_count = await db.scan_history.count_documents({"risk_level": "warning"})
    safe_count = await db.scan_history.count_documents({"risk_level": "safe"})

    return {
        "total_scans": total,
        "phishing_detected": phishing,
        "legitimate_detected": legitimate,
        "url_scans": url_scans,
        "email_scans": email_scans,
        "risk_breakdown": {
            "danger": danger_count,
            "warning": warning_count,
            "safe": safe_count,
        },
        "detection_rate": round((phishing / total * 100), 2) if total > 0 else 0,
    }
