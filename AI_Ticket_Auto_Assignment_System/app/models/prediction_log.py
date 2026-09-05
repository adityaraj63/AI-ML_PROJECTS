"""
Prediction Log Model — records every AI prediction made
"""
from datetime import datetime, timezone
from ..extensions import db


class PredictionLog(db.Model):
    __tablename__ = "prediction_logs"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    model_version = db.Column(db.String(50), nullable=True)

    # Input
    input_text = db.Column(db.Text, nullable=False)
    cleaned_text = db.Column(db.Text, nullable=True)

    # Output
    predicted_dept = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    all_probabilities = db.Column(db.Text, nullable=True)  # JSON string
    predicted_priority = db.Column(db.String(20), nullable=True)
    estimated_resolution_hours = db.Column(db.Float, nullable=True)
    keywords_detected = db.Column(db.Text, nullable=True)  # JSON string

    # Feedback
    is_correct = db.Column(db.Boolean, nullable=True)
    corrected_dept = db.Column(db.String(100), nullable=True)
    feedback_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    feedback_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    feedback_by = db.relationship("User", foreign_keys=[feedback_by_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "model_name": self.model_name,
            "predicted_dept": self.predicted_dept,
            "confidence_score": self.confidence_score,
            "predicted_priority": self.predicted_priority,
            "is_correct": self.is_correct,
            "created_at": self.created_at.isoformat(),
        }


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    extra_data = db.Column(db.Text, nullable=True)  # JSON
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user.full_name if self.user else "System",
            "action": self.action,
            "description": self.description,
            "ticket_id": self.ticket_id,
            "created_at": self.created_at.isoformat(),
        }
