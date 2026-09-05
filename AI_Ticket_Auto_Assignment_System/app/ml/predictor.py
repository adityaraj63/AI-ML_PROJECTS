"""
Prediction Service
Loads the trained model and provides real-time predictions with confidence scores,
priority estimation, resolution time, and keyword extraction.
"""
import os
import json
import logging
import joblib
import numpy as np
from typing import Dict, Any, Optional

from .preprocessor import preprocess, extract_keywords

logger = logging.getLogger(__name__)

# ── Priority & resolution time heuristics ─────────────────────────────────────
PRIORITY_KEYWORDS = {
    "critical": ["crash", "down", "breach", "ransomware", "unauthorized", "production", "outage", "failure", "breach"],
    "high": ["urgent", "cannot", "failed", "lost", "error", "broken", "blocked", "immediately", "escalat"],
    "medium": ["slow", "issue", "problem", "not working", "intermittent", "sometimes"],
    "low": ["request", "would like", "suggestion", "minor", "enhancement", "question"],
}

DEPT_RESOLUTION_HOURS = {
    "Hardware": 8,
    "Software": 4,
    "Network": 2,
    "Database": 6,
    "Cloud": 4,
    "Security": 1,
    "HR": 24,
    "Finance": 48,
    "CRM Support": 12,
    "DevOps": 3,
}


class PredictionService:
    """Singleton prediction service that loads and caches the model."""

    _instance: Optional["PredictionService"] = None

    def __new__(cls, model_dir: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_dir: str = None):
        if self._initialized:
            return
        self._model_dir = model_dir or self._default_model_dir()
        self._pipeline = None
        self._metadata = None
        self._load_model()
        self._initialized = True

    @staticmethod
    def _default_model_dir() -> str:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base, "app", "ml", "saved_models")

    def _load_model(self):
        """Load model pipeline and metadata from disk."""
        model_path = os.path.join(self._model_dir, "best_model.pkl")
        meta_path = os.path.join(self._model_dir, "model_metadata.json")

        if not os.path.exists(model_path):
            logger.warning("No trained model found at %s. Please run train-model.", model_path)
            self._pipeline = None
            self._metadata = None
            return

        self._pipeline = joblib.load(model_path)
        logger.info("Model loaded from %s", model_path)

        if os.path.exists(meta_path):
            with open(meta_path) as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {}

    def reload(self):
        """Force reload the model (call after retraining)."""
        self._load_model()

    @property
    def is_model_loaded(self) -> bool:
        return self._pipeline is not None

    @property
    def model_name(self) -> str:
        if self._metadata:
            return self._metadata.get("best_model_name", "Unknown")
        return "Unknown"

    @property
    def labels(self):
        if self._metadata:
            return self._metadata.get("labels", [])
        return []

    @property
    def best_metrics(self) -> dict:
        if self._metadata:
            return self._metadata.get("best_metrics", {})
        return {}

    @property
    def all_metrics(self) -> dict:
        if self._metadata:
            return self._metadata.get("metrics", {})
        return {}

    def predict(self, title: str, description: str) -> Dict[str, Any]:
        """
        Predict department for a ticket.

        Returns:
            {
                "predicted_department": str,
                "confidence": float,
                "all_probabilities": dict,
                "priority": str,
                "estimated_hours": float,
                "keywords": list[str],
                "cleaned_text": str,
                "model_name": str,
                "success": bool,
                "message": str,
            }
        """
        if not self.is_model_loaded:
            return {
                "success": False,
                "message": "Model not trained yet. Please run the training pipeline.",
                "predicted_department": None,
                "confidence": 0.0,
                "all_probabilities": {},
                "priority": "medium",
                "estimated_hours": 24.0,
                "keywords": [],
                "cleaned_text": "",
                "model_name": "None",
            }

        combined = f"{title} {description}"
        cleaned = preprocess(combined)
        keywords = extract_keywords(combined, top_n=6)

        # Predict
        predicted_dept = self._pipeline.predict([cleaned])[0]

        # Probability scores
        all_probs = {}
        try:
            proba = self._pipeline.predict_proba([cleaned])[0]
            classes = self._pipeline.classes_
            all_probs = {cls: round(float(p), 4) for cls, p in zip(classes, proba)}
            confidence = float(max(proba))
        except AttributeError:
            confidence = 0.95
            all_probs = {predicted_dept: confidence}

        # Priority heuristic
        priority = self._estimate_priority(combined.lower())

        # Resolution time
        base_hours = DEPT_RESOLUTION_HOURS.get(predicted_dept, 24)
        priority_multipliers = {"critical": 0.25, "high": 0.5, "medium": 1.0, "low": 2.0}
        estimated_hours = round(base_hours * priority_multipliers.get(priority, 1.0), 1)

        return {
            "success": True,
            "message": "Prediction successful",
            "predicted_department": predicted_dept,
            "confidence": round(confidence * 100, 2),
            "all_probabilities": all_probs,
            "priority": priority,
            "estimated_hours": estimated_hours,
            "keywords": keywords,
            "cleaned_text": cleaned,
            "model_name": self.model_name,
        }

    def _estimate_priority(self, text: str) -> str:
        """Simple keyword-based priority estimation."""
        for priority in ["critical", "high", "medium", "low"]:
            if any(kw in text for kw in PRIORITY_KEYWORDS[priority]):
                return priority
        return "medium"

    def find_similar(self, title: str, description: str, top_n: int = 3):
        """
        Return the top department probabilities — used for 'similar ticket' suggestions.
        """
        result = self.predict(title, description)
        if not result["success"]:
            return []
        sorted_probs = sorted(
            result["all_probabilities"].items(), key=lambda x: x[1], reverse=True
        )
        return [{"department": dept, "confidence": round(p * 100, 2)} for dept, p in sorted_probs[:top_n]]


# Global singleton instance
_service_instance: Optional[PredictionService] = None


def get_prediction_service() -> PredictionService:
    """Get or create the global prediction service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = PredictionService()
    return _service_instance
