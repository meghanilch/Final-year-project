from fastapi import APIRouter
from datetime import datetime, timezone
from app.models.schemas import EmailScanRequest
from app.ml.predictor import predict_email
from app.core.database import get_db

router = APIRouter()


@router.post("/")
async def scan_email(request: EmailScanRequest):
    result = predict_email(request.subject, request.body, request.sender)

    doc = {
        "scan_type": "email",
        "subject": request.subject,
        "sender": request.sender,
        "prediction": result["prediction"],
        "risk_level": result["risk_level"],
        "phishing_score": result["phishing_score"],
        "indicators": result["indicators"],
        "urls_found": result["urls_found"],
        "created_at": datetime.now(timezone.utc),
    }
    db = get_db()
    inserted = await db.scan_history.insert_one(doc)
    result["id"] = str(inserted.inserted_id)

    return result
