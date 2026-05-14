from fastapi import APIRouter
from app.core.database import get_db

router = APIRouter()


def _default_stats():
    return {
        "total_scans": 0,
        "phishing_detected": 0,
        "legitimate_detected": 0,
        "url_scans": 0,
        "email_scans": 0,
        "risk_breakdown": {
            "danger": 0,
            "warning": 0,
            "safe": 0,
        },
        "detection_rate": 0,
    }


@router.get("/")
async def get_stats():
    db = get_db()
    if db is None:
        return _default_stats()

    try:
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
    except Exception:
        return _default_stats()
