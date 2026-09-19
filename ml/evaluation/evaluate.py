import json
import joblib
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from ml.training.train import generate_synthetic_benchmark_data
from ml.features.feature_pipeline import FEATURE_NAMES

def evaluate():
    model_path = "ml/models/repurposing_model.joblib"
    try:
        model = joblib.load(model_path)
    except Exception as e:
        print(f"Could not load model from {model_path}: {e}")
        return

    X, y = generate_synthetic_benchmark_data(n_samples=300, random_state=123)
    y_pred_proba = model.predict_proba(X)[:, 1]
    y_pred = model.predict(X)

    auc = roc_auc_score(y, y_pred_proba)
    report = classification_report(y, y_pred, output_dict=True)
    cm = confusion_matrix(y, y_pred).tolist()

    # Feature importances
    importances = model.feature_importances_
    feat_importance_dict = {
        feat: round(float(imp), 4)
        for feat, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True)
    }

    eval_results = {
        "auc_roc": round(auc, 4),
        "confusion_matrix": cm,
        "classification_report": report,
        "feature_importances": feat_importance_dict
    }

    print("=== MODEL EVALUATION RESULTS ===")
    print(json.dumps(eval_results, indent=2))
    return eval_results

if __name__ == "__main__":
    evaluate()
