"""
ML package init
"""
from .predictor import get_prediction_service, PredictionService

__all__ = ["get_prediction_service", "PredictionService"]
