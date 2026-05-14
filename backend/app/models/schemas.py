from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Any
from datetime import datetime


class URLScanRequest(BaseModel):
    url: str

class EmailScanRequest(BaseModel):
    subject: str
    body: str
    sender: Optional[str] = ""

class ScanResult(BaseModel):
    id: Optional[str] = None
    scan_type: str  # "url" or "email"
    prediction: str
    risk_level: str
    confidence: Optional[float] = None
    phishing_score: Optional[float] = None
    indicators: List[str] = []
    created_at: Optional[datetime] = None
    raw: Optional[dict] = None
