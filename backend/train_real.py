"""
train_real.py — PhishGuard AI Real Dataset Trainer
Loads real phishing + legitimate URLs, trains Random Forest,
saves model + full performance report.

Run AFTER download_datasets.py
"""

import os, sys, csv, re, pickle, warnings, random
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, accuracy_score,
    precision_score, recall_score, f1_score,
    roc_curve
)

DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Inline Feature Extractor (self-contained, no import needed) ───────────────
import math
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
    c = Counter(s)
    t = len(s)
    return -sum((v/t)*math.log2(v/t) for v in c.values())

def extract_features(url):
    url = str(url).strip()
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
    url_len  = len(url)
    num_digits   = sum(c.isdigit() for c in url)
    num_hyphens  = url.count("-")
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

# ── 1. Load Datasets ──────────────────────────────────────────────────────────
def load_phishing_urls(max_per_source=30000):
    urls = []

    # PhishTank CSV
    pt_path = os.path.join(DATA_DIR, "phishtank.csv")
    if os.path.exists(pt_path):
        count = 0
        with open(pt_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = row.get("url","").strip()
                if u and u.startswith("http"):
                    urls.append(u)
                    count += 1
                    if count >= max_per_source: break
        print(f"   📂 PhishTank CSV     : {count:>6} phishing URLs")

    # OpenPhish text feed
    op_path = os.path.join(DATA_DIR, "openphish.txt")
    if os.path.exists(op_path):
        count = 0
        with open(op_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                u = line.strip()
                if u and u.startswith("http"):
                    urls.append(u)
                    count += 1
                    if count >= max_per_source: break
        print(f"   📂 OpenPhish feed    : {count:>6} phishing URLs")

    # URLhaus CSV
    uh_path = os.path.join(DATA_DIR, "urlhaus.csv")
    if os.path.exists(uh_path):
        count = 0
        with open(uh_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#"): continue
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    u = parts[2].strip().strip('"')
                    if u and u.startswith("http"):
                        urls.append(u)
                        count += 1
                        if count >= max_per_source: break
        print(f"   📂 URLhaus feed      : {count:>6} malicious URLs")

    # Deduplicate
    urls = list(set(urls))
    random.shuffle(urls)
    print(f"   ✅ Total phishing (deduped): {len(urls)}")
    return urls

def load_legitimate_urls(max_per_source=30000):
    urls = []

    def domain_to_url(domain):
        d = domain.strip().lower()
        if not d: return None
        if d.startswith("http"): return d
        return "https://www." + d

    # Tranco
    tr_path = os.path.join(DATA_DIR, "tranco.csv")
    if os.path.exists(tr_path):
        count = 0
        with open(tr_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 2:
                    u = domain_to_url(row[1])
                    if u:
                        urls.append(u)
                        count += 1
                        if count >= max_per_source: break
        print(f"   📂 Tranco Top-1M     : {count:>6} legitimate URLs")

    # Cisco Umbrella
    um_path = os.path.join(DATA_DIR, "umbrella.csv")
    if os.path.exists(um_path):
        count = 0
        with open(um_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    u = domain_to_url(row[1])
                    if u:
                        urls.append(u)
                        count += 1
                        if count >= max_per_source: break
        print(f"   📂 Cisco Umbrella    : {count:>6} legitimate URLs")

    urls = list(set(urls))
    random.shuffle(urls)
    print(f"   ✅ Total legitimate (deduped): {len(urls)}")
    return urls

# ── 2. Build Feature Matrix ───────────────────────────────────────────────────
def build_features(phishing_urls, legit_urls, max_each=25000):
    print(f"\n⚙️  Extracting features...")
    print(f"   Processing up to {max_each:,} phishing + {max_each:,} legitimate URLs")

    rows = []
    errors = 0

    sample_phish = phishing_urls[:max_each]
    sample_legit = legit_urls[:max_each]

    for i, url in enumerate(sample_phish):
        try:
            f = extract_features(url)
            f["label"] = 1
            rows.append(f)
        except: errors += 1
        if (i+1) % 5000 == 0:
            print(f"   🔴 Phishing processed: {i+1:,}/{len(sample_phish):,}")

    for i, url in enumerate(sample_legit):
        try:
            f = extract_features(url)
            f["label"] = 0
            rows.append(f)
        except: errors += 1
        if (i+1) % 5000 == 0:
            print(f"   🟢 Legitimate processed: {i+1:,}/{len(sample_legit):,}")

    df = pd.DataFrame(rows)
    print(f"\n   ✅ Feature matrix built:")
    print(f"      Rows (URLs)     : {len(df):,}")
    print(f"      Columns (feats) : {len(FEATURE_COLUMNS)}")
    print(f"      Phishing        : {(df.label==1).sum():,}")
    print(f"      Legitimate      : {(df.label==0).sum():,}")
    print(f"      Errors skipped  : {errors}")
    return df

# ── 3. Train Model ────────────────────────────────────────────────────────────
def train(df):
    X = df[FEATURE_COLUMNS].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"\n🔀 Train / Test Split:")
    print(f"   Training : {len(X_train):,} URLs")
    print(f"   Testing  : {len(X_test):,} URLs")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators      = 300,
            max_depth         = 20,
            min_samples_split = 2,
            min_samples_leaf  = 1,
            max_features      = "sqrt",
            class_weight      = "balanced",
            random_state      = 42,
            n_jobs            = -1,
        ))
    ])

    # Cross validation
    print(f"\n🔁 Running 5-Fold Cross-Validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1  = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1",       n_jobs=-1)
    cv_acc = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
    print(f"   CV F1 per fold   : {[round(s,4) for s in cv_f1]}")
    print(f"   CV Mean F1       : {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")
    print(f"   CV Mean Accuracy : {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")

    print(f"\n🤖 Training final model...")
    pipeline.fit(X_train, y_train)
    print(f"   ✅ Done!")

    # Evaluate
    y_pred      = pipeline.predict(X_test)
    y_pred_prob = pipeline.predict_proba(X_test)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec  = recall_score(y_test, y_pred, zero_division=0)
    f1   = f1_score(y_test, y_pred, zero_division=0)
    auc  = roc_auc_score(y_test, y_pred_prob)
    cm   = confusion_matrix(y_test, y_pred)

    print(f"\n{'='*60}")
    print(f"  📊 FINAL MODEL RESULTS")
    print(f"{'='*60}")
    print(f"  Accuracy    : {acc*100:.2f}%")
    print(f"  Precision   : {prec*100:.2f}%")
    print(f"  Recall      : {rec*100:.2f}%")
    print(f"  F1-Score    : {f1*100:.2f}%")
    print(f"  ROC-AUC     : {auc*100:.2f}%")
    print(f"\n  Confusion Matrix:")
    print(f"                 Pred Legit   Pred Phish")
    print(f"  Actual Legit   {cm[0][0]:>10,}   {cm[0][1]:>10,}")
    print(f"  Actual Phish   {cm[1][0]:>10,}   {cm[1][1]:>10,}")
    tn,fp,fn,tp = cm.ravel()
    print(f"\n  TP (Phishing caught)     : {tp:,}")
    print(f"  TN (Legitimate passed)   : {tn:,}")
    print(f"  FP (Legitimate flagged)  : {fp:,}  ← false alarms")
    print(f"  FN (Phishing missed)     : {fn:,}  ← dangerous misses")
    print(f"\n  Full Classification Report:")
    print(classification_report(y_test, y_pred,
          target_names=["Legitimate","Phishing"]))

    # Feature importance
    rf = pipeline.named_steps["clf"]
    feat_imp = sorted(zip(FEATURE_COLUMNS, rf.feature_importances_), key=lambda x:-x[1])
    print(f"\n🏆 Top 10 Most Important Features:")
    print(f"   {'Feature':<28} {'Importance':>10}  Bar")
    print(f"   {'-'*55}")
    for feat, imp in feat_imp[:10]:
        bar = "█" * int(imp * 300)
        print(f"   {feat:<28} {imp:>10.4f}  {bar}")

    return pipeline, feat_imp, (y_test, y_pred, y_pred_prob), (acc, prec, rec, f1, auc), cm

# ── 4. Save Model ─────────────────────────────────────────────────────────────
def save_model(pipeline, n_urls):
    path = os.path.join(OUTPUT_DIR, "phishing_model_real.pkl")
    with open(path, "wb") as f:
        pickle.dump(pipeline, f)
    size_mb = os.path.getsize(path) / (1024*1024)
    print(f"\n💾 Model saved → {path}")
    print(f"   Size    : {size_mb:.2f} MB")
    print(f"   Trained : {n_urls:,} URLs")
    return path

# ── 5. Save Report Charts ─────────────────────────────────────────────────────
def save_charts(feat_imp, eval_data, metrics, cm):
    y_test, y_pred, y_proba = eval_data
    acc, prec, rec, f1, auc = metrics

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor("#0D1117")
    for ax in axes.flat:
        ax.set_facecolor("#1E2A3A")
        ax.tick_params(colors="white")
        for sp in ax.spines.values(): sp.set_edgecolor("#4A5568")

    # Chart 1: Feature Importance
    ax = axes[0][0]
    top = feat_imp[:14]
    names  = [f[0] for f in top]
    vals   = [f[1] for f in top]
    colors = ["#00E5FF" if v > 0.05 else "#2E75B6" for v in vals]
    bars = ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    ax.set_title("Top 14 Feature Importances", color="white", fontweight="bold", fontsize=12)
    ax.set_xlabel("Importance", color="#8899B4")
    ax.tick_params(axis="y", labelcolor="white", labelsize=8)
    ax.tick_params(axis="x", labelcolor="#8899B4")
    for bar, val in zip(bars, vals[::-1]):
        ax.text(bar.get_width()+0.001, bar.get_y()+bar.get_height()/2,
                f"{val:.3f}", va="center", color="white", fontsize=7)

    # Chart 2: Confusion Matrix
    ax = axes[0][1]
    labels = [["TN\nLegitimate\ncorrect","FP\nLegitimate\nwrongly flagged"],
              ["FN\nPhishing\nmissed","TP\nPhishing\ncaught"]]
    cm_cols = [["#00E676","#FF3B5C"],["#FFAB00","#00E5FF"]]
    for i in range(2):
        for j in range(2):
            ax.add_patch(plt.Rectangle((j,1-i),1,1,color=cm_cols[i][j],alpha=0.85))
            val = cm[i][j]
            ax.text(j+0.5, 1.55-i, f"{val:,}", ha="center", va="center",
                    fontsize=16, fontweight="bold", color="white")
            ax.text(j+0.5, 1.3-i, labels[i][j], ha="center", va="center",
                    fontsize=7, color="white", alpha=0.9)
    ax.set_xlim(0,2); ax.set_ylim(0,2)
    ax.set_xticks([0.5,1.5]); ax.set_xticklabels(["Predicted Legit","Predicted Phish"], color="white")
    ax.set_yticks([0.5,1.5]); ax.set_yticklabels(["Actual Phish","Actual Legit"], color="white")
    ax.set_title("Confusion Matrix", color="white", fontweight="bold", fontsize=12)
    ax.tick_params(length=0)

    # Chart 3: ROC Curve
    ax = axes[1][0]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    ax.plot(fpr, tpr, color="#00E5FF", lw=2, label=f"ROC (AUC = {auc:.4f})")
    ax.plot([0,1],[0,1], color="#4A5568", linestyle="--", lw=1)
    ax.fill_between(fpr, tpr, alpha=0.15, color="#00E5FF")
    ax.set_xlabel("False Positive Rate", color="#8899B4")
    ax.set_ylabel("True Positive Rate",  color="#8899B4")
    ax.set_title("ROC Curve", color="white", fontweight="bold", fontsize=12)
    ax.tick_params(colors="#8899B4")
    ax.legend(facecolor="#1E2A3A", labelcolor="white", fontsize=10)

    # Chart 4: Performance Metrics
    ax = axes[1][1]
    metric_names = ["Accuracy","Precision","Recall","F1-Score","ROC-AUC"]
    metric_vals  = [acc, prec, rec, f1, auc]
    bar_colors   = ["#00E5FF","#00E676","#FFAB00","#BF80FF","#FF3B5C"]
    bars4 = ax.bar(metric_names, [v*100 for v in metric_vals],
                   color=bar_colors, width=0.6)
    ax.set_ylim(0, 115)
    ax.set_title("Model Performance", color="white", fontweight="bold", fontsize=12)
    ax.set_ylabel("Score (%)", color="#8899B4")
    ax.tick_params(axis="x", labelcolor="white", labelsize=9)
    ax.tick_params(axis="y", labelcolor="#8899B4")
    ax.axhline(y=90, color="#4A5568", linestyle="--", lw=1, alpha=0.5, label="90% baseline")
    for bar, val in zip(bars4, metric_vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                f"{val*100:.1f}%", ha="center", color="white", fontsize=9, fontweight="bold")

    plt.suptitle("PhishGuard AI — Real Dataset Training Report",
                 color="white", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "real_training_report.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
    plt.close()
    print(f"📈 Charts saved → {path}")

# ── 6. Save Text Report ───────────────────────────────────────────────────────
def save_text_report(n_total, n_phish, n_legit, metrics, cv_f1, feat_imp, cm):
    acc, prec, rec, f1, auc = metrics
    tn, fp, fn, tp = cm.ravel()
    path = os.path.join(OUTPUT_DIR, "training_report.txt")
    with open(path, "w") as f:
        f.write("="*60 + "\n")
        f.write("  PHISHGUARD AI — REAL DATASET TRAINING REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"DATASET\n")
        f.write(f"  Total URLs    : {n_total:,}\n")
        f.write(f"  Phishing      : {n_phish:,}\n")
        f.write(f"  Legitimate    : {n_legit:,}\n")
        f.write(f"  Features      : {len(FEATURE_COLUMNS)}\n\n")
        f.write(f"CROSS-VALIDATION (5-Fold)\n")
        f.write(f"  F1 per fold   : {[round(s,4) for s in cv_f1]}\n")
        f.write(f"  Mean F1       : {cv_f1.mean():.4f}\n\n")
        f.write(f"TEST SET RESULTS\n")
        f.write(f"  Accuracy      : {acc*100:.2f}%\n")
        f.write(f"  Precision     : {prec*100:.2f}%\n")
        f.write(f"  Recall        : {rec*100:.2f}%\n")
        f.write(f"  F1-Score      : {f1*100:.2f}%\n")
        f.write(f"  ROC-AUC       : {auc*100:.2f}%\n\n")
        f.write(f"CONFUSION MATRIX\n")
        f.write(f"  True  Positives (phishing caught)    : {tp:,}\n")
        f.write(f"  True  Negatives (legitimate passed)  : {tn:,}\n")
        f.write(f"  False Positives (false alarms)       : {fp:,}\n")
        f.write(f"  False Negatives (phishing missed)    : {fn:,}\n\n")
        f.write(f"TOP 10 FEATURES\n")
        for i,(feat,imp) in enumerate(feat_imp[:10], 1):
            f.write(f"  {i:2}. {feat:<28} {imp:.4f}\n")
        f.write("\n" + "="*60 + "\n")
    print(f"📄 Report saved → {path}")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PHISHGUARD AI — REAL DATASET TRAINER")
    print("="*60)

    # Check data folder
    if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
        print(f"\n❌ No data found in {DATA_DIR}")
        print("   Run download_datasets.py first!")
        sys.exit(1)

    print(f"\n📂 Loading real phishing URLs...")
    phishing_urls = load_phishing_urls(max_per_source=30000)

    print(f"\n📂 Loading legitimate URLs...")
    legit_urls = load_legitimate_urls(max_per_source=30000)

    if len(phishing_urls) < 100 or len(legit_urls) < 100:
        print(f"\n❌ Not enough data:")
        print(f"   Phishing   : {len(phishing_urls)} (need 100+)")
        print(f"   Legitimate : {len(legit_urls)} (need 100+)")
        print("   Run download_datasets.py to get real data first.")
        sys.exit(1)

    # Balance dataset
    max_each = min(len(phishing_urls), len(legit_urls), 25000)
    print(f"\n⚖️  Balancing: using {max_each:,} URLs from each class")

    df = build_features(phishing_urls, legit_urls, max_each=max_each)

    pipeline, feat_imp, eval_data, metrics, cm = train(df)
    y_test, y_pred, y_proba = eval_data
    acc, prec, rec, f1, auc = metrics

    # Cross-val scores for report
    X = df[FEATURE_COLUMNS].values
    y = df["label"].values
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1 = cross_val_score(pipeline, X_tr, y_tr, cv=cv, scoring="f1", n_jobs=-1)

    model_path = save_model(pipeline, len(df))
    save_charts(feat_imp, eval_data, metrics, cm)
    save_text_report(len(df), (df.label==1).sum(), (df.label==0).sum(),
                     metrics, cv_f1, feat_imp, cm)

    print(f"\n{'='*60}")
    print(f"  ✅ TRAINING COMPLETE!")
    print(f"{'='*60}")
    print(f"  Trained on   : {len(df):,} real URLs")
    print(f"  Accuracy     : {acc*100:.2f}%")
    print(f"  F1-Score     : {f1*100:.2f}%")
    print(f"  ROC-AUC      : {auc*100:.2f}%")
    print(f"\n  📁 Files to copy to your project:")
    print(f"     {model_path}")
    print(f"     → backend/app/ml/models/phishing_model_real.pkl")
    print(f"\n  ⚙️  Update backend/.env:")
    print(f"     MODEL_PATH=app/ml/models/phishing_model_real.pkl")
    print(f"{'='*60}\n")
