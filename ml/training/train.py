import os
import json
import joblib
import numpy as np
from datetime import datetime, timezone
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score

from ml.features.feature_pipeline import FEATURE_NAMES

def generate_synthetic_benchmark_data(n_samples: int = 500, random_state: int = 42):
    """Generate documented benchmark dataset representing historical repurposing outcomes."""
    rng = np.random.RandomState(random_state)
    
    # 15 features corresponding to FEATURE_NAMES
    X = np.zeros((n_samples, len(FEATURE_NAMES)))
    
    # Clinical trials: 0 to 20
    X[:, 0] = rng.poisson(lam=4, size=n_samples)
    # Phase 1, 2, 3, 4
    X[:, 1] = rng.binomial(n=X[:, 0].astype(int), p=0.4)
    X[:, 2] = rng.binomial(n=X[:, 0].astype(int), p=0.3)
    X[:, 3] = rng.binomial(n=X[:, 0].astype(int), p=0.2)
    X[:, 4] = rng.binomial(n=X[:, 0].astype(int), p=0.1)
    # Completed
    X[:, 5] = rng.binomial(n=X[:, 0].astype(int), p=0.6)
    # Total enrollment log
    X[:, 6] = np.log1p(X[:, 0] * rng.uniform(20, 200, size=n_samples))
    # Literature count
    X[:, 7] = rng.poisson(lam=12, size=n_samples)
    X[:, 8] = rng.binomial(n=X[:, 7].astype(int), p=0.15)  # meta-analysis
    X[:, 9] = rng.binomial(n=X[:, 7].astype(int), p=0.20)  # RCT
    X[:, 10] = rng.binomial(n=X[:, 7].astype(int), p=0.35) # Observational
    # Patents
    X[:, 11] = rng.poisson(lam=3, size=n_samples)
    X[:, 12] = rng.binomial(n=X[:, 11].astype(int), p=0.5)  # granted
    # Market signals
    X[:, 13] = rng.poisson(lam=2, size=n_samples)
    X[:, 14] = rng.choice([0.0, 1.0], size=n_samples, p=[0.2, 0.8])

    # Ground truth: probability of repurposing success correlates with Phase 3/4 trials, meta-analyses, and granted patents
    logits = (
        0.8 * X[:, 3] +   # Phase 3
        1.2 * X[:, 4] +   # Phase 4
        0.5 * X[:, 8] +   # Meta-analysis
        0.4 * X[:, 9] +   # RCT
        0.3 * X[:, 12] +  # Granted patents
        0.1 * X[:, 6] -   # Enrollment log
        1.5
    )
    probs = 1.0 / (1.0 + np.exp(-logits))
    y = (rng.uniform(0, 1, size=n_samples) < probs).astype(int)

    return X, y

def train():
    os.makedirs("ml/models", exist_ok=True)
    X, y = generate_synthetic_benchmark_data(n_samples=800)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    auc = float(roc_auc_score(y_test, y_pred_proba))
    f1 = float(f1_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))

    model_path = "ml/models/repurposing_model.joblib"
    joblib.dump(model, model_path)

    metadata = {
        "model_type": "RandomForestClassifier",
        "feature_names": FEATURE_NAMES,
        "n_samples": len(X),
        "test_metrics": {
            "auc_roc": round(auc, 4),
            "f1_score": round(f1, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4)
        },
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model_version": "1.0.0",
        "disclaimer": "Trained on documented synthetic benchmark repurposing dataset for research support."
    }

    with open("ml/models/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model successfully trained and saved to {model_path}")
    print(f"Metrics: AUC={auc:.4f}, F1={f1:.4f}, Precision={prec:.4f}, Recall={rec:.4f}")

if __name__ == "__main__":
    train()
