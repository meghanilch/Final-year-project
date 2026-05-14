import re
import numpy as np
from app.ml.feature_extractor import extract_features, FEATURE_COLUMNS
from app.ml.trainer import get_model

SUSPICIOUS_EMAIL_PATTERNS = [
    r"urgent.{0,30}action",
    r"verify.{0,20}account",
    r"click.{0,30}link",
    r"suspended.{0,20}account",
    r"confirm.{0,20}password",
    r"update.{0,20}billing",
    r"won.{0,20}prize",
    r"free.{0,30}gift",
    r"unusual.{0,20}activity",
    r"security.{0,20}alert",
    r"limited.{0,20}time",
    r"act.{0,20}now",
    r"bank.{0,20}details",
    r"social security",
    r"reset.{0,20}password.{0,20}immediately",
]

PHISHING_EMAIL_DOMAINS = [
    "noreply-secure", "support-alert", "account-verify", "login-confirm",
    "security-update", "billing-notice"
]


def predict_url(url: str) -> dict:
    model = get_model()
    features = extract_features(url)
    X = np.array([[features[col] for col in FEATURE_COLUMNS]])
    prob = model.predict_proba(X)[0]
    pred = int(model.predict(X)[0])

    confidence = float(round(prob[pred] * 100, 2))
    phishing_prob = float(round(prob[1] * 100, 2))

    risk_level = "safe"
    if phishing_prob >= 75:
        risk_level = "danger"
    elif phishing_prob >= 45:
        risk_level = "warning"

    indicators = []
    if features["has_ip"]:
        indicators.append("IP address used instead of domain name")
    if features["suspicious_tld"]:
        indicators.append("Suspicious top-level domain detected")
    if features["has_phishing_keyword"]:
        indicators.append(f"Contains {features['keyword_count']} phishing keyword(s)")
    if features["has_encoding"]:
        indicators.append("URL contains percent-encoded characters")
    if features["num_subdomains"] > 2:
        indicators.append("Excessive number of subdomains")
    if features["hostname_entropy"] > 3.8:
        indicators.append("High entropy hostname (may be randomised)")
    if features["is_shortener"]:
        indicators.append("URL shortener detected — destination hidden")
    if features["has_redirect"]:
        indicators.append("URL redirect chain detected")
    if features["double_slash"]:
        indicators.append("Double slash in URL path")
    if not features["is_https"]:
        indicators.append("Not using secure HTTPS connection")
    if features["num_hyphens"] > 3:
        indicators.append("Multiple hyphens in URL (common in phishing)")

    return {
        "url": url,
        "prediction": "phishing" if pred == 1 else "legitimate",
        "risk_level": risk_level,
        "phishing_probability": phishing_prob,
        "confidence": confidence,
        "indicators": indicators,
        "features": features,
    }


def predict_email(subject: str, body: str, sender: str = "") -> dict:
    text = f"{subject} {body}".lower()

    matched_patterns = []
    for pattern in SUSPICIOUS_EMAIL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            matched_patterns.append(pattern.replace(r".{0,30}", "...").replace(r"\\", ""))

    urls_in_body = re.findall(r"https?://[^\s\"'>]+", body)
    url_results = [predict_url(u) for u in urls_in_body[:5]]
    phishing_urls = [r for r in url_results if r["prediction"] == "phishing"]

    suspicious_domain = any(d in sender.lower() for d in PHISHING_EMAIL_DOMAINS)
    has_urgency = bool(re.search(r"\burgent\b|\bimmediately\b|\bwarning\b|\bsuspend", text, re.I))
    has_credential_request = bool(re.search(r"password|ssn|credit card|bank account|social security", text, re.I))

    score = 0
    score += len(matched_patterns) * 10
    score += len(phishing_urls) * 25
    score += 20 if suspicious_domain else 0
    score += 15 if has_urgency else 0
    score += 20 if has_credential_request else 0
    score = min(score, 100)

    risk_level = "safe"
    if score >= 70:
        risk_level = "danger"
    elif score >= 35:
        risk_level = "warning"

    indicators = []
    if matched_patterns:
        indicators.append(f"Contains {len(matched_patterns)} suspicious phrase(s)")
    if phishing_urls:
        indicators.append(f"{len(phishing_urls)} phishing URL(s) found in body")
    if suspicious_domain:
        indicators.append("Sender domain looks suspicious")
    if has_urgency:
        indicators.append("Email uses urgency or threat language")
    if has_credential_request:
        indicators.append("Requests sensitive personal/financial information")
    if len(urls_in_body) > 5:
        indicators.append(f"Unusually high number of links ({len(urls_in_body)})")

    return {
        "subject": subject,
        "sender": sender,
        "prediction": "phishing" if score >= 50 else "legitimate",
        "risk_level": risk_level,
        "phishing_score": score,
        "indicators": indicators,
        "urls_found": len(urls_in_body),
        "phishing_urls": phishing_urls,
        "matched_patterns": matched_patterns,
    }
