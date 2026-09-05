"""
Models package — exports all models for convenience
"""
from .user import User
from .department import Department
from .ticket import Ticket, TicketComment
from .prediction_log import PredictionLog, ActivityLog

__all__ = ["User", "Department", "Ticket", "TicketComment", "PredictionLog", "ActivityLog"]
