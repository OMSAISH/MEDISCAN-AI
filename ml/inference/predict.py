import os
import joblib
import numpy as np
from typing import Dict, Any, List
from ml.features.feature_pipeline import feature_pipeline, FEATURE_NAMES

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/repurposing_model.joblib"))

class MLPredictor:
    """Provides inference and feature attribution for repurposing candidate indications."""

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception:
                self.model = None

    def predict(
        self,
        trials: List[Dict[str, Any]],
        publications: List[Dict[str, Any]],
        patents: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        features = feature_pipeline.extract_features(trials, publications, patents, market_data)
        
        if self.model is None:
            self._load_model()

        if self.model is not None:
            proba = float(self.model.predict_proba(features.reshape(1, -1))[0, 1])
            # Simple attribution based on feature * importance
            importances = getattr(self.model, "feature_importances_", None)
            attributions = {}
            if importances is not None:
                for name, val, imp in zip(FEATURE_NAMES, features, importances):
                    attributions[name] = round(float(val * imp), 4)
            return {
                "model_available": True,
                "repurposing_signal_probability": round(proba, 4),
                "feature_attributions": attributions,
                "model_version": "1.0.0"
            }
        else:
            return {
                "model_available": False,
                "repurposing_signal_probability": None,
                "message": "Model weights not yet trained or loaded."
            }

ml_predictor = MLPredictor()
