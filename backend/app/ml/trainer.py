"""
trainer.py — PhishGuard AI Model Trainer (Upgraded v2)
Trains Random Forest with cross-validation, feature importance, and full report.
"""
import os, sys, pickle, warnings
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "phishing_model_v2.pkl")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))
from feature_extractor import extract_features, FEATURE_COLUMNS
from dataset import PHISHING_URLS, LEGITIMATE_URLS

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, accuracy_score,
    precision_score, recall_score, f1_score
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_PATH = os.path.join(OUTPUT_DIR, "phishing_model_v2.pkl")

# ── 1. Build Dataset ──────────────────────────────────────────────────────────
def build_dataset():
    print("\n" + "="*60)
    print("  PHISHGUARD AI — MODEL TRAINER v2")
    print("="*60)
    print(f"\n📦 Building dataset...")
    rows = []
    errors = 0
    for url in PHISHING_URLS:
        try:
            f = extract_features(url)
            f["label"] = 1
            f["url"]   = url
            rows.append(f)
        except:
            errors += 1
    for url in LEGITIMATE_URLS:
        try:
            f = extract_features(url)
            f["label"] = 0
            f["url"]   = url
            rows.append(f)
        except:
            errors += 1
    df = pd.DataFrame(rows)
    print(f"   ✅ Total URLs loaded : {len(df)}")
    print(f"   🔴 Phishing          : {(df.label==1).sum()}")
    print(f"   🟢 Legitimate        : {(df.label==0).sum()}")
    print(f"   ⚠️  Extraction errors : {errors}")
    print(f"   📊 Features per URL  : {len(FEATURE_COLUMNS)}")
    return df

# ── 2. Feature Analysis ───────────────────────────────────────────────────────
def show_feature_stats(df):
    print(f"\n📊 Feature Statistics (mean by class):")
    print(f"{'Feature':<25} {'Phishing':>10} {'Legitimate':>12} {'Diff':>8}")
    print("-"*57)
    phish = df[df.label==1]
    legit = df[df.label==0]
    diffs = []
    for col in FEATURE_COLUMNS:
        pm = phish[col].mean()
        lm = legit[col].mean()
        diff = abs(pm - lm)
        diffs.append((col, pm, lm, diff))
    for col, pm, lm, diff in sorted(diffs, key=lambda x: -x[3])[:15]:
        print(f"   {col:<23} {pm:>10.3f} {lm:>12.3f} {diff:>8.3f}")

# ── 3. Train Model ────────────────────────────────────────────────────────────
def train(df):
    X = df[FEATURE_COLUMNS].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\n🔀 Train/Test Split:")
    print(f"   Training samples : {len(X_train)}")
    print(f"   Testing samples  : {len(X_test)}")

    # ── Pipeline ──────────────────────────────────────────────────────────────
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators   = 300,
            max_depth      = 15,
            min_samples_split = 2,
            min_samples_leaf  = 1,
            max_features   = "sqrt",
            class_weight   = "balanced",
            random_state   = 42,
            n_jobs         = -1,
        ))
    ])

    # ── Cross-Validation ──────────────────────────────────────────────────────
    print(f"\n🔁 Running 5-Fold Cross-Validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)
    print(f"   CV F1 Scores     : {[round(s,4) for s in cv_scores]}")
    print(f"   CV Mean F1       : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    cv_acc = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
    print(f"   CV Mean Accuracy : {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")

    # ── Final Training ────────────────────────────────────────────────────────
    print(f"\n🤖 Training final model on full training set...")
    pipeline.fit(X_train, y_train)
    print(f"   ✅ Training complete!")

    # ── Evaluation ────────────────────────────────────────────────────────────
    y_pred      = pipeline.predict(X_test)
    y_pred_prob = pipeline.predict_proba(X_test)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec  = recall_score(y_test, y_pred)
    f1   = f1_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_pred_prob)

    print(f"\n{'='*60}")
    print(f"  MODEL EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"   Accuracy    : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"   Precision   : {prec:.4f}  ({prec*100:.2f}%)")
    print(f"   Recall      : {rec:.4f}  ({rec*100:.2f}%)")
    print(f"   F1-Score    : {f1:.4f}  ({f1*100:.2f}%)")
    print(f"   ROC-AUC     : {auc:.4f}  ({auc*100:.2f}%)")
    print(f"\n   Classification Report:")
    print(classification_report(y_test, y_pred,
          target_names=["Legitimate","Phishing"]))

    # ── Confusion Matrix ──────────────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)
    print(f"   Confusion Matrix:")
    print(f"                  Predicted")
    print(f"                  Legit  Phishing")
    print(f"   Actual Legit   {cm[0][0]:>5}  {cm[0][1]:>8}")
    print(f"   Actual Phish   {cm[1][0]:>5}  {cm[1][1]:>8}")

    tn, fp, fn, tp = cm.ravel()
    print(f"\n   True  Positives (TP) : {tp}  ← phishing correctly caught")
    print(f"   True  Negatives (TN) : {tn}  ← legitimate correctly passed")
    print(f"   False Positives (FP) : {fp}  ← legitimate wrongly flagged")
    print(f"   False Negatives (FN) : {fn}  ← phishing missed (dangerous!)")

    # ── Feature Importance ────────────────────────────────────────────────────
    rf_model = pipeline.named_steps["clf"]
    importances = rf_model.feature_importances_
    feat_imp = sorted(zip(FEATURE_COLUMNS, importances), key=lambda x: -x[1])

    print(f"\n🏆 Top 10 Most Important Features:")
    print(f"   {'Feature':<28} {'Importance':>10}")
    print(f"   {'-'*40}")
    for feat, imp in feat_imp[:10]:
        bar = "█" * int(imp * 200)
        print(f"   {feat:<28} {imp:>10.4f}  {bar}")

    return pipeline, feat_imp, (y_test, y_pred, y_pred_prob), (acc, prec, rec, f1, auc)

# ── 4. Save Model ─────────────────────────────────────────────────────────────
def save_model(pipeline):
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)
    size_kb = os.path.getsize(MODEL_PATH) / 1024
    print(f"\n💾 Model saved → {MODEL_PATH}")
    print(f"   File size: {size_kb:.1f} KB")

# ── 5. Plot Charts ────────────────────────────────────────────────────────────
def plot_charts(feat_imp, eval_data, metrics):
    y_test, y_pred, y_pred_prob = eval_data
    acc, prec, rec, f1, auc = metrics

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor("#0D1117")
    for ax in axes:
        ax.set_facecolor("#1E2A3A")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#4A5568")

    # ── Chart 1: Feature Importance ───────────────────────────────────────────
    top_features = feat_imp[:12]
    names  = [f[0] for f in top_features]
    values = [f[1] for f in top_features]
    colors = ["#00E5FF" if v > 0.05 else "#2E75B6" for v in values]
    bars = axes[0].barh(names[::-1], values[::-1], color=colors[::-1], edgecolor="none")
    axes[0].set_title("Top 12 Feature Importances", color="white", fontsize=13, fontweight="bold", pad=10)
    axes[0].set_xlabel("Importance Score", color="#8899B4")
    axes[0].tick_params(axis="y", labelcolor="white", labelsize=9)
    axes[0].tick_params(axis="x", labelcolor="#8899B4")
    for bar, val in zip(bars, values[::-1]):
        axes[0].text(bar.get_width()+0.001, bar.get_y()+bar.get_height()/2,
                     f"{val:.3f}", va="center", color="white", fontsize=8)

    # ── Chart 2: Confusion Matrix ─────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)
    cm_colors = [["#00E676","#FF3B5C"],["#FF3B5C","#00E676"]]
    for i in range(2):
        for j in range(2):
            axes[1].add_patch(plt.Rectangle((j,1-i),1,1, color=cm_colors[i][j], alpha=0.8))
            axes[1].text(j+0.5, 1.5-i, str(cm[i][j]), ha="center", va="center",
                        fontsize=22, fontweight="bold", color="white")
    axes[1].set_xlim(0,2); axes[1].set_ylim(0,2)
    axes[1].set_xticks([0.5,1.5]); axes[1].set_xticklabels(["Pred: Legit","Pred: Phish"], color="white")
    axes[1].set_yticks([0.5,1.5]); axes[1].set_yticklabels(["Actual: Phish","Actual: Legit"], color="white")
    axes[1].set_title("Confusion Matrix", color="white", fontsize=13, fontweight="bold", pad=10)
    axes[1].tick_params(axis="both", length=0)

    # ── Chart 3: Metrics Bar Chart ────────────────────────────────────────────
    metric_names = ["Accuracy","Precision","Recall","F1-Score","ROC-AUC"]
    metric_vals  = [acc, prec, rec, f1, auc]
    bar_colors   = ["#00E5FF","#00E676","#FFAB00","#BF80FF","#FF3B5C"]
    bars3 = axes[2].bar(metric_names, [v*100 for v in metric_vals],
                        color=bar_colors, edgecolor="none", width=0.6)
    axes[2].set_ylim(0, 110)
    axes[2].set_title("Model Performance Metrics", color="white", fontsize=13, fontweight="bold", pad=10)
    axes[2].set_ylabel("Score (%)", color="#8899B4")
    axes[2].tick_params(axis="x", labelcolor="white", labelsize=9)
    axes[2].tick_params(axis="y", labelcolor="#8899B4")
    axes[2].axhline(y=90, color="#4A5568", linestyle="--", linewidth=1, alpha=0.5)
    for bar, val in zip(bars3, metric_vals):
        axes[2].text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5,
                     f"{val*100:.1f}%", ha="center", color="white", fontsize=10, fontweight="bold")

    plt.suptitle("PhishGuard AI — Model Training Report", color="white",
                 fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()

    chart_path = os.path.join(OUTPUT_DIR, "training_report.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight",
                facecolor="#0D1117", edgecolor="none")
    plt.close()
    print(f"📈 Training charts saved → {chart_path}")

# ── 6. Test on New Examples ───────────────────────────────────────────────────
def test_examples(pipeline):
    print(f"\n{'='*60}")
    print(f"  LIVE PREDICTION TEST")
    print(f"{'='*60}")
    test_urls = [
        ("http://paypal-secure-login.xyz/verify?id=123", "phishing"),
        ("http://192.168.1.1/admin/login.php",           "phishing"),
        ("http://amazon-prize-winner.click/claim",       "phishing"),
        ("http://login-apple-id.ml/verify-account",      "phishing"),
        ("http://bit.ly/free-iphone-winner2024",         "phishing"),
        ("https://www.google.com",                       "legitimate"),
        ("https://github.com/user/repo",                 "legitimate"),
        ("https://stackoverflow.com/questions/123",      "legitimate"),
        ("https://www.paypal.com/home",                  "legitimate"),
        ("https://www.amazon.com/products",              "legitimate"),
    ]
    print(f"\n   {'URL':<45} {'Expected':<12} {'Predicted':<12} {'Prob':>6}  {'✓'}")
    print(f"   {'-'*85}")
    correct = 0
    for url, expected in test_urls:
        feats = extract_features(url)
        X = np.array([[feats[col] for col in FEATURE_COLUMNS]])
        prob  = pipeline.predict_proba(X)[0][1]
        pred  = "phishing" if prob >= 0.5 else "legitimate"
        match = "✅" if pred == expected else "❌"
        if pred == expected: correct += 1
        url_short = url[:44] + "…" if len(url) > 45 else url
        print(f"   {url_short:<45} {expected:<12} {pred:<12} {prob:>5.1%}  {match}")
    print(f"\n   Result: {correct}/{len(test_urls)} correct  ({correct/len(test_urls)*100:.0f}%)")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = build_dataset()
    show_feature_stats(df)
    pipeline, feat_imp, eval_data, metrics = train(df)
    save_model(pipeline)
    plot_charts(feat_imp, eval_data, metrics)
    test_examples(pipeline)

    print(f"\n{'='*60}")
    print(f"  ✅ TRAINING COMPLETE!")
    print(f"  Model: {MODEL_PATH}")
    print(f"  Copy phishing_model_v2.pkl → backend/app/ml/models/")
    print(f"  Update MODEL_PATH in config.py to phishing_model_v2.pkl")
    print(f"{'='*60}\n")
def get_model():
    import pickle
    import os

    model_path = os.path.join(
        os.path.dirname(__file__),
        "output",   # because your model is saved here
        "phishing_model_v2.pkl"
    )

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. Run trainer.py first."
        )

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    return model
def ensure_model_trained():
    import os
    
    model_path = os.path.join(
        os.path.dirname(__file__),
        "output",
        "phishing_model_v2.pkl"
    )

    if not os.path.exists(model_path):
        print("⚠️ Model not found. Training now...")
        
        df = build_dataset()
        pipeline, _, _, _ = train(df)
        save_model(pipeline)

        print("✅ Model trained successfully!")
    else:
        print("✅ Model already exists.")
    