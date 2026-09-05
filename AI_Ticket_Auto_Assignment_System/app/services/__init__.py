"""
Services package
"""
from .ticket_service import (
    create_ticket,
    get_ticket_by_id,
    get_ticket_by_number,
    update_ticket_status,
    assign_ticket,
    correct_ai_prediction,
    add_comment,
    search_tickets,
)
from .analytics_service import (
    get_dashboard_stats,
    get_tickets_per_department,
    get_tickets_per_month,
    get_priority_distribution,
    get_department_workload,
    get_all_charts_data,
    get_recent_activity,
)

__all__ = [
    "create_ticket",
    "get_ticket_by_id",
    "get_ticket_by_number",
    "update_ticket_status",
    "assign_ticket",
    "correct_ai_prediction",
    "add_comment",
    "search_tickets",
    "get_dashboard_stats",
    "get_tickets_per_department",
    "get_tickets_per_month",
    "get_priority_distribution",
    "get_department_workload",
    "get_all_charts_data",
    "get_recent_activity",
]
