"""
Department Model
"""
from datetime import datetime, timezone
from ..extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    icon = db.Column(db.String(50), default="bi-building", nullable=False)
    color = db.Column(db.String(20), default="#6366f1", nullable=False)
    sla_hours = db.Column(db.Integer, default=24, nullable=False)  # SLA in hours
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    tickets = db.relationship("Ticket", foreign_keys="[Ticket.department_id]", backref="department", lazy="dynamic")
    head = db.relationship("User", foreign_keys=[head_id], backref="headed_department")

    @property
    def open_ticket_count(self) -> int:
        return self.tickets.filter_by(status="open").count()

    @property
    def total_ticket_count(self) -> int:
        return self.tickets.count()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "email": self.email,
            "icon": self.icon,
            "color": self.color,
            "sla_hours": self.sla_hours,
            "is_active": self.is_active,
            "open_tickets": self.open_ticket_count,
            "total_tickets": self.total_ticket_count,
        }

    def __repr__(self) -> str:
        return f"<Department {self.name}>"
