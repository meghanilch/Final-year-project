"""
download_datasets.py — PhishGuard AI
Downloads 3 real phishing datasets automatically.
Run this ONCE before training.

Datasets used:
  1. PhishTank    — verified phishing URLs (community-reported)
  2. OpenPhish    — active phishing feed (auto-updated)
  3. Tranco List  — top 1 million legitimate domains
"""

import os, sys, csv, json, gzip, urllib.request, urllib.error

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def download(url, dest, label):
    print(f"  ⬇️  Downloading {label}...")
    try:
        headers = {"User-Agent": "Mozilla/5.0 PhishGuard-Research/1.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            while True:
                chunk = r.read(8192)
                if not chunk: break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r     {pct:.1f}%  ({downloaded//1024} KB)", end="", flush=True)
        print(f"\r  ✅ {label} saved → {dest}                    ")
        return True
    except Exception as e:
        print(f"\r  ❌ {label} failed: {e}")
        return False

def get_phishtank(max_urls=50000):
    """PhishTank verified phishing URLs — free, no login needed for basic feed"""
    dest = os.path.join(DATA_DIR, "phishtank.csv")
    if os.path.exists(dest):
        print(f"  ✅ PhishTank already downloaded → {dest}")
        return dest

    # Try the public JSON feed (no API key needed)
    url = "http://data.phishtank.com/data/online-valid.json.gz"
    gz_dest = dest + ".gz"
    if download(url, gz_dest, "PhishTank JSON"):
        try:
            with gzip.open(gz_dest, "rt", encoding="utf-8") as f:
                data = json.load(f)
            with open(dest, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["url", "label"])
                count = 0
                for entry in data:
                    if entry.get("verified") == "yes" and entry.get("online") == "yes":
                        writer.writerow([entry["url"], 1])
                        count += 1
                        if count >= max_urls: break
            print(f"  📊 Extracted {count} verified phishing URLs from PhishTank")
            os.remove(gz_dest)
            return dest
        except Exception as e:
            print(f"  ❌ Parse error: {e}")

    # Fallback: CSV feed
    url2 = "http://data.phishtank.com/data/online-valid.csv.bz2"
    if download(url2, dest + ".bz2", "PhishTank CSV"):
        import bz2
        with bz2.open(dest + ".bz2", "rt", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            with open(dest, "w", newline="", encoding="utf-8") as out:
                writer = csv.writer(out)
                writer.writerow(["url", "label"])
                count = 0
                for row in reader:
                    if row.get("verified") == "yes":
                        writer.writerow([row["url"], 1])
                        count += 1
                        if count >= max_urls: break
        print(f"  📊 Extracted {count} phishing URLs")
        return dest
    return None

def get_openphish():
    """OpenPhish free feed — active phishing URLs"""
    dest = os.path.join(DATA_DIR, "openphish.txt")
    if os.path.exists(dest):
        print(f"  ✅ OpenPhish already downloaded → {dest}")
        return dest
    url = "https://openphish.com/feed.txt"
    if download(url, dest, "OpenPhish feed"):
        with open(dest) as f:
            count = sum(1 for line in f if line.strip())
        print(f"  📊 {count} OpenPhish URLs")
        return dest
    return None

def get_urlhaus():
    """URLhaus — malicious URLs (includes phishing)"""
    dest = os.path.join(DATA_DIR, "urlhaus.csv")
    if os.path.exists(dest):
        print(f"  ✅ URLhaus already downloaded → {dest}")
        return dest
    url = "https://urlhaus.abuse.ch/downloads/csv_recent/"
    if download(url, dest, "URLhaus recent"):
        with open(dest) as f:
            count = sum(1 for line in f if line.strip() and not line.startswith("#"))
        print(f"  📊 {count} URLhaus entries")
        return dest
    return None

def get_tranco(max_urls=50000):
    """Tranco Top 1M domains — legitimate websites"""
    dest = os.path.join(DATA_DIR, "tranco.csv")
    if os.path.exists(dest):
        print(f"  ✅ Tranco already downloaded → {dest}")
        return dest
    url = "https://tranco-list.eu/download/XKGZ/full"
    gz_dest = dest + ".gz"
    if download(url, gz_dest, "Tranco Top-1M"):
        try:
            with gzip.open(gz_dest, "rt") as f:
                with open(dest, "w", newline="") as out:
                    writer = csv.writer(out)
                    writer.writerow(["rank", "domain"])
                    for i, line in enumerate(f):
                        writer.writerow(line.strip().split(",", 1))
                        if i >= max_urls: break
            os.remove(gz_dest)
            return dest
        except:
            pass
    # Fallback: direct CSV
    url2 = "https://tranco-list.eu/download_daily/XKGZ"
    if download(url2, dest, "Tranco CSV"):
        return dest
    # Last resort: Alexa mirror
    url3 = "https://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
    zip_dest = dest + ".zip"
    if download(url3, zip_dest, "Alexa Top-1M"):
        import zipfile
        with zipfile.ZipFile(zip_dest) as z:
            with z.open(z.namelist()[0]) as zf:
                with open(dest, "wb") as out:
                    out.write(zf.read())
        os.remove(zip_dest)
        return dest
    return None

def get_cisco_umbrella(max_urls=50000):
    """Cisco Umbrella Top 1M — very trusted legitimate domains"""
    dest = os.path.join(DATA_DIR, "umbrella.csv")
    if os.path.exists(dest):
        print(f"  ✅ Umbrella already downloaded → {dest}")
        return dest
    url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
    zip_dest = dest + ".zip"
    if download(url, zip_dest, "Cisco Umbrella Top-1M"):
        import zipfile
        try:
            with zipfile.ZipFile(zip_dest) as z:
                with z.open("top-1m.csv") as zf:
                    content = zf.read().decode("utf-8", errors="ignore")
            with open(dest, "w") as f:
                f.write(content)
            os.remove(zip_dest)
            count = min(sum(1 for _ in open(dest)), max_urls)
            print(f"  📊 {count} Umbrella domains")
            return dest
        except Exception as e:
            print(f"  ❌ Extract error: {e}")
    return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PHISHGUARD AI — REAL DATASET DOWNLOADER")
    print("="*60)
    print("\n📥 Downloading phishing datasets...")
    pt  = get_phishtank()
    op  = get_openphish()
    uh  = get_urlhaus()
    print("\n📥 Downloading legitimate URL datasets...")
    tr  = get_tranco()
    um  = get_cisco_umbrella()

    print("\n" + "="*60)
    print("  DOWNLOAD SUMMARY")
    print("="*60)
    results = [
        ("PhishTank (phishing)",         pt),
        ("OpenPhish (phishing)",          op),
        ("URLhaus (malicious)",           uh),
        ("Tranco Top-1M (legitimate)",    tr),
        ("Cisco Umbrella (legitimate)",   um),
    ]
    for name, path in results:
        status = f"✅ {path}" if path else "❌ Failed"
        print(f"  {name:<35} {status}")

    downloaded = sum(1 for _, p in results if p)
    print(f"\n  {downloaded}/{len(results)} datasets ready")
    print(f"  Data folder: {DATA_DIR}")
    if downloaded >= 2:
        print("\n  ✅ Ready to train! Run: python3 train_real.py")
    else:
        print("\n  ⚠️  Not enough data. Check internet and retry.")
    print("="*60 + "\n")
