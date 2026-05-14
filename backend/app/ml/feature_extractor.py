"""
feature_extractor.py — PhishGuard AI (Upgraded v2)
33 features extracted from a URL string.
"""
import re, math
from urllib.parse import urlparse, parse_qs
from collections import Counter

PHISHING_KEYWORDS = [
    "login","signin","verify","update","secure","account","bank",
    "paypal","ebay","amazon","apple","google","microsoft","confirm",
    "password","credential","billing","suspend","unusual","alert",
    "support","free","winner","click","urgent","limited","expire",
    "validate","authorize","checkout","recover","reset","unlock",
    "service","notice","important",
]
SUSPICIOUS_TLDS = {".xyz",".tk",".ml",".ga",".cf",".gq",".pw",".top",
    ".club",".work",".link",".click",".info",".biz",".online",
    ".site",".tech",".live",".stream",".download",".win"}
TRUSTED_TLDS = {".com",".org",".net",".edu",".gov",".io",".co",
    ".uk",".us",".ca",".au",".de",".fr",".jp"}
SHORTENERS = {"bit.ly","tinyurl.com","goo.gl","t.co","ow.ly",
    "is.gd","buff.ly","adf.ly","shorte.st","bc.vc","cutt.ly"}
SUSPICIOUS_BRANDS = [
    "paypal","google","facebook","apple","amazon","microsoft",
    "netflix","instagram","twitter","linkedin","dropbox","ebay",
    "chase","wellsfargo","bankofamerica","citibank","hsbc",
    "irs","usps","fedex","dhl","steam","coinbase","binance","metamask",
]

def shannon_entropy(s):
    if not s: return 0.0
    counts = Counter(s)
    total = len(s)
    return -sum((c/total)*math.log2(c/total) for c in counts.values())

def extract_features(url):
    url = url.strip()
    try:
        parsed = urlparse(url if url.startswith("http") else "http://"+url)
    except:
        parsed = urlparse("http://invalid")
    hostname = (parsed.hostname or "").lower()
    path     = parsed.path or ""
    query    = parsed.query or ""
    full     = url.lower()
    parts    = hostname.split(".")
    tld      = ("."+parts[-1]) if len(parts)>=2 else ""

    url_len = len(url)
    num_digits = sum(c.isdigit() for c in url)
    num_hyphens = url.count("-")
    hostname_len = len(hostname)

    brand_host = hostname.replace(parts[-1],"").replace(parts[-2] if len(parts)>=2 else "","")

    return {
        "url_length":           url_len,
        "hostname_length":      hostname_len,
        "path_length":          len(path),
        "query_length":         len(query),
        "num_dots":             url.count("."),
        "num_hyphens":          num_hyphens,
        "num_at":               url.count("@"),
        "num_question":         url.count("?"),
        "num_ampersand":        url.count("&"),
        "num_equals":           url.count("="),
        "num_slashes":          url.count("/"),
        "num_digits":           num_digits,
        "num_subdomains":       max(0, len(parts)-2),
        "num_params":           len(parse_qs(query)),
        "num_fragments":        1 if parsed.fragment else 0,
        "has_ip":               1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname) else 0,
        "is_https":             1 if parsed.scheme=="https" else 0,
        "has_port":             1 if parsed.port else 0,
        "has_encoding":         1 if "%" in url else 0,
        "double_slash":         1 if "//" in path else 0,
        "has_redirect":         1 if full.count("http")>1 else 0,
        "is_shortener":         1 if any(s in hostname for s in SHORTENERS) else 0,
        "suspicious_tld":       1 if tld in SUSPICIOUS_TLDS else 0,
        "trusted_tld":          1 if tld in TRUSTED_TLDS else 0,
        "keyword_count":        sum(1 for kw in PHISHING_KEYWORDS if kw in full),
        "has_phishing_keyword": 1 if any(kw in full for kw in PHISHING_KEYWORDS) else 0,
        "brand_in_subdomain":   1 if any(b in brand_host for b in SUSPICIOUS_BRANDS) else 0,
        "brand_count":          sum(1 for b in SUSPICIOUS_BRANDS if b in full),
        "hostname_entropy":     round(shannon_entropy(hostname), 4),
        "path_entropy":         round(shannon_entropy(path), 4),
        "digit_ratio":          round(num_digits/max(url_len,1), 4),
        "hyphen_ratio":         round(num_hyphens/max(hostname_len,1), 4),
    }

FEATURE_COLUMNS = list(extract_features("http://example.com").keys())