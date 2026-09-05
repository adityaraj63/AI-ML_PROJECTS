"""
User Model
Supports three roles: employee, agent (supervisor), admin
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(
        db.Enum("employee", "agent", "admin", name="user_roles"),
        nullable=False,
        default="employee",
    )
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    department = db.relationship("Department", backref="members", foreign_keys=[department_id])
    tickets_created = db.relationship(
        "Ticket", backref="creator", foreign_keys="Ticket.created_by_id", lazy="dynamic"
    )
    tickets_assigned = db.relationship(
        "Ticket", backref="assignee", foreign_keys="Ticket.assigned_to_id", lazy="dynamic"
    )
    activity_logs = db.relationship("ActivityLog", backref="user", lazy="dynamic")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def display_role(self) -> str:
        role_map = {"employee": "Employee", "agent": "Support Agent", "admin": "Administrator"}
        return role_map.get(self.role, self.role)

    @property
    def avatar_initials(self) -> str:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    def update_last_login(self):
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "department": self.department.name if self.department else None,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"
