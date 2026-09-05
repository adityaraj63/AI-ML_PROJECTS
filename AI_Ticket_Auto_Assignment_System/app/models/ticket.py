"""
Ticket Model
"""
from datetime import datetime, timezone
from ..extensions import db


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # Content
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Classification
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    priority = db.Column(
        db.Enum("low", "medium", "high", "critical", name="ticket_priority"),
        default="medium",
        nullable=False,
    )
    status = db.Column(
        db.Enum("open", "in_progress", "resolved", "closed", "escalated", name="ticket_status"),
        default="open",
        nullable=False,
        index=True,
    )
    category = db.Column(db.String(100), nullable=True)

    # People
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # AI Prediction
    ai_predicted_dept_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True)
    ai_priority = db.Column(db.String(20), nullable=True)
    ai_estimated_hours = db.Column(db.Float, nullable=True)
    ai_keywords = db.Column(db.Text, nullable=True)  # JSON string
    is_ai_prediction_correct = db.Column(db.Boolean, nullable=True)

    # Meta
    resolution_notes = db.Column(db.Text, nullable=True)
    is_duplicate = db.Column(db.Boolean, default=False)
    duplicate_of_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    resolved_at = db.Column(db.DateTime, nullable=True)
    due_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    ai_predicted_dept = db.relationship("Department", foreign_keys=[ai_predicted_dept_id])
    prediction_logs = db.relationship("PredictionLog", backref="ticket", lazy="dynamic")
    activity_logs = db.relationship("ActivityLog", backref="ticket", lazy="dynamic")
    comments = db.relationship("TicketComment", backref="ticket", lazy="dynamic", cascade="all, delete-orphan")

    PRIORITY_COLORS = {
        "low": "#22c55e",
        "medium": "#f59e0b",
        "high": "#ef4444",
        "critical": "#7c3aed",
    }

    STATUS_COLORS = {
        "open": "#3b82f6",
        "in_progress": "#f59e0b",
        "resolved": "#22c55e",
        "closed": "#6b7280",
        "escalated": "#ef4444",
    }

    @property
    def priority_color(self) -> str:
        return self.PRIORITY_COLORS.get(self.priority, "#6b7280")

    @property
    def status_color(self) -> str:
        return self.STATUS_COLORS.get(self.status, "#6b7280")

    @property
    def is_overdue(self) -> bool:
        if self.due_at and self.status not in ("resolved", "closed"):
            return datetime.now(timezone.utc) > self.due_at.replace(tzinfo=timezone.utc)
        return False

    @property
    def resolution_time_hours(self) -> float | None:
        if self.resolved_at and self.created_at:
            delta = self.resolved_at - self.created_at.replace(tzinfo=None)
            return round(delta.total_seconds() / 3600, 2)
        return None

    @staticmethod
    def generate_ticket_number() -> str:
        import random, string
        prefix = "TKT"
        suffix = "".join(random.choices(string.digits, k=6))
        ts = datetime.now(timezone.utc).strftime("%m%d")
        return f"{prefix}-{ts}-{suffix}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ticket_number": self.ticket_number,
            "title": self.title,
            "description": self.description,
            "department": self.department.name if self.department else None,
            "priority": self.priority,
            "status": self.status,
            "created_by": self.creator.full_name if self.creator else None,
            "assigned_to": self.assignee.full_name if self.assignee else None,
            "ai_confidence": self.ai_confidence,
            "ai_keywords": self.ai_keywords,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_number}: {self.title[:30]}>"


class TicketComment(db.Model):
    __tablename__ = "ticket_comments"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref="comments")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user.full_name,
            "content": self.content,
            "is_internal": self.is_internal,
            "created_at": self.created_at.isoformat(),
        }
