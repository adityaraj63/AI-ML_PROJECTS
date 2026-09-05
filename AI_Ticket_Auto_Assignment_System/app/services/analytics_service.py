"""
Analytics Service — aggregates data for dashboards and reports
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, extract

from ..extensions import db
from ..models.ticket import Ticket
from ..models.department import Department
from ..models.user import User
from ..models.prediction_log import PredictionLog, ActivityLog

logger = logging.getLogger(__name__)


def get_dashboard_stats() -> dict:
    """Get overall statistics for admin dashboard."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total = Ticket.query.count()
    open_count = Ticket.query.filter_by(status="open").count()
    in_progress = Ticket.query.filter_by(status="in_progress").count()
    resolved = Ticket.query.filter_by(status="resolved").count()
    closed = Ticket.query.filter_by(status="closed").count()
    today = Ticket.query.filter(Ticket.created_at >= today_start).count()

    # Prediction accuracy
    total_logs = PredictionLog.query.filter(PredictionLog.is_correct.isnot(None)).count()
    correct_logs = PredictionLog.query.filter_by(is_correct=True).count()
    accuracy = round((correct_logs / total_logs * 100), 1) if total_logs > 0 else None

    # Average resolution time
    resolved_tickets = Ticket.query.filter(
        Ticket.resolved_at.isnot(None),
        Ticket.created_at.isnot(None),
    ).all()
    avg_resolution = None
    if resolved_tickets:
        times = [
            (t.resolved_at - t.created_at).total_seconds() / 3600
            for t in resolved_tickets
            if t.resolved_at and t.created_at
        ]
        avg_resolution = round(sum(times) / len(times), 1) if times else None

    # Overdue tickets
    overdue = Ticket.query.filter(
        Ticket.due_at < now,
        Ticket.status.notin_(["resolved", "closed"]),
    ).count()

    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed,
        "today": today,
        "overdue": overdue,
        "prediction_accuracy": accuracy,
        "avg_resolution_hours": avg_resolution,
    }


def get_tickets_per_department() -> dict:
    """Returns ticket counts per department for charts."""
    results = (
        db.session.query(Department.name, func.count(Ticket.id))
        .join(Ticket, Ticket.department_id == Department.id, isouter=True)
        .group_by(Department.name)
        .all()
    )
    return {name: count for name, count in results}


def get_tickets_per_month(months: int = 12) -> dict:
    """Ticket volume by month for the last N months."""
    results = (
        db.session.query(
            extract('year', Ticket.created_at).label("year"),
            extract('month', Ticket.created_at).label("month"),
            func.count(Ticket.id).label("count"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return {
        f"{month_names[int(row.month) - 1]} {int(row.year)}": row.count
        for row in results[-months:]
    }


def get_priority_distribution() -> dict:
    """Ticket counts by priority."""
    results = (
        db.session.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )
    return {priority: count for priority, count in results}


def get_status_distribution() -> dict:
    """Ticket counts by status."""
    results = (
        db.session.query(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
        .all()
    )
    return {status: count for status, count in results}


def get_department_workload() -> list:
    """Department workload including open/resolved/in-progress counts."""
    departments = Department.query.filter_by(is_active=True).all()
    workload = []
    for dept in departments:
        workload.append({
            "name": dept.name,
            "color": dept.color,
            "icon": dept.icon,
            "open": dept.tickets.filter_by(status="open").count(),
            "in_progress": dept.tickets.filter_by(status="in_progress").count(),
            "resolved": dept.tickets.filter_by(status="resolved").count(),
            "total": dept.total_ticket_count,
        })
    return sorted(workload, key=lambda x: x["total"], reverse=True)


def get_agent_performance() -> list:
    """Agent performance metrics."""
    agents = User.query.filter_by(role="agent", is_active=True).all()
    performance = []
    for agent in agents:
        assigned = agent.tickets_assigned.count()
        resolved = agent.tickets_assigned.filter_by(status="resolved").count()
        rate = round(resolved / assigned * 100, 1) if assigned > 0 else 0.0
        performance.append({
            "agent": agent.full_name,
            "assigned": assigned,
            "resolved": resolved,
            "resolution_rate": rate,
        })
    return sorted(performance, key=lambda x: x["resolved"], reverse=True)


def get_prediction_accuracy_trend() -> dict:
    """Prediction accuracy over time."""
    results = (
        db.session.query(
            extract('year', PredictionLog.created_at).label("year"),
            extract('month', PredictionLog.created_at).label("month"),
            func.sum(
                db.case((PredictionLog.is_correct == True, 1), else_=0)
            ).label("correct"),
            func.count(PredictionLog.id).label("total"),
        )
        .filter(PredictionLog.is_correct.isnot(None))
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    trend = {}
    for row in results:
        label = f"{month_names[int(row.month) - 1]} {int(row.year)}"
        trend[label] = round(row.correct / row.total * 100, 1) if row.total > 0 else 0
    return trend


def get_recent_activity(limit: int = 20) -> list:
    """Recent system activity for the timeline."""
    logs = (
        ActivityLog.query
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [log.to_dict() for log in logs]


def get_all_charts_data() -> dict:
    """Bundle all chart data into one response."""
    return {
        "tickets_per_department": get_tickets_per_department(),
        "tickets_per_month": get_tickets_per_month(),
        "priority_distribution": get_priority_distribution(),
        "status_distribution": get_status_distribution(),
        "prediction_accuracy_trend": get_prediction_accuracy_trend(),
    }
