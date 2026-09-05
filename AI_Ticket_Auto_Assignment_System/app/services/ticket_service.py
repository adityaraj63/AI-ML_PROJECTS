"""
Ticket Service — business logic for ticket CRUD, AI prediction, and search
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple

from flask import request as flask_request
from sqlalchemy import or_, and_

from ..extensions import db
from ..models.ticket import Ticket, TicketComment
from ..models.department import Department
from ..models.prediction_log import PredictionLog, ActivityLog
from ..models.user import User
from ..ml.predictor import get_prediction_service

logger = logging.getLogger(__name__)


def create_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    created_by: User = None,
    run_ai: bool = True,
) -> Tuple[Ticket, Optional[dict]]:
    """
    Create a new ticket with optional AI prediction.
    Returns (ticket, prediction_result).
    """
    ticket = Ticket(
        ticket_number=Ticket.generate_ticket_number(),
        title=title.strip(),
        description=description.strip(),
        priority=priority,
        status="open",
        created_by_id=created_by.id if created_by else None,
    )

    prediction_result = None
    if run_ai:
        try:
            service = get_prediction_service()
            result = service.predict(title, description)
            if result["success"]:
                prediction_result = result
                dept = Department.query.filter_by(name=result["predicted_department"]).first()
                if dept:
                    ticket.department_id = dept.id
                ticket.ai_predicted_dept_id = dept.id if dept else None
                ticket.ai_confidence = result["confidence"]
                ticket.ai_priority = result["priority"]
                ticket.ai_estimated_hours = result["estimated_hours"]
                ticket.ai_keywords = json.dumps(result["keywords"])

                # Set due date based on SLA
                if dept and dept.sla_hours:
                    ticket.due_at = datetime.now(timezone.utc) + timedelta(hours=dept.sla_hours)
        except Exception as e:
            logger.error("AI prediction failed: %s", e)

    db.session.add(ticket)
    db.session.flush()

    # Log prediction
    if prediction_result:
        log = PredictionLog(
            ticket_id=ticket.id,
            model_name=prediction_result.get("model_name", "Unknown"),
            input_text=f"{title} {description}",
            cleaned_text=prediction_result.get("cleaned_text", ""),
            predicted_dept=prediction_result.get("predicted_department", "Unknown"),
            confidence_score=prediction_result.get("confidence", 0.0),
            all_probabilities=json.dumps(prediction_result.get("all_probabilities", {})),
            predicted_priority=prediction_result.get("priority", "medium"),
            estimated_resolution_hours=prediction_result.get("estimated_hours"),
            keywords_detected=json.dumps(prediction_result.get("keywords", [])),
        )
        db.session.add(log)

    # Activity log
    _log_activity(
        user_id=created_by.id if created_by else None,
        ticket_id=ticket.id,
        action="ticket_created",
        description=f"Ticket {ticket.ticket_number} created",
    )

    db.session.commit()
    return ticket, prediction_result


def get_ticket_by_number(ticket_number: str) -> Optional[Ticket]:
    return Ticket.query.filter_by(ticket_number=ticket_number).first()


def get_ticket_by_id(ticket_id: int) -> Optional[Ticket]:
    return db.session.get(Ticket, ticket_id)


def update_ticket_status(
    ticket: Ticket,
    new_status: str,
    user: User = None,
    resolution_notes: str = None,
) -> Ticket:
    old_status = ticket.status
    ticket.status = new_status
    if new_status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = datetime.now(timezone.utc)
    if resolution_notes:
        ticket.resolution_notes = resolution_notes

    _log_activity(
        user_id=user.id if user else None,
        ticket_id=ticket.id,
        action="status_updated",
        description=f"Status changed from {old_status} to {new_status}",
    )
    db.session.commit()
    return ticket


def assign_ticket(ticket: Ticket, agent_id: int, user: User = None) -> Ticket:
    ticket.assigned_to_id = agent_id
    if ticket.status == "open":
        ticket.status = "in_progress"
    _log_activity(
        user_id=user.id if user else None,
        ticket_id=ticket.id,
        action="ticket_assigned",
        description=f"Ticket assigned to agent ID {agent_id}",
    )
    db.session.commit()
    return ticket


def correct_ai_prediction(
    ticket: Ticket,
    correct_dept_name: str,
    user: User = None,
) -> Ticket:
    dept = Department.query.filter_by(name=correct_dept_name).first()
    if dept:
        ticket.department_id = dept.id
        ticket.is_ai_prediction_correct = False

        # Update prediction log
        log = ticket.prediction_logs.order_by(PredictionLog.created_at.desc()).first()
        if log:
            log.is_correct = False
            log.corrected_dept = correct_dept_name
            log.feedback_by_id = user.id if user else None
            log.feedback_at = datetime.now(timezone.utc)

    _log_activity(
        user_id=user.id if user else None,
        ticket_id=ticket.id,
        action="prediction_corrected",
        description=f"AI prediction corrected to {correct_dept_name}",
    )
    db.session.commit()
    return ticket


def add_comment(
    ticket: Ticket,
    user: User,
    content: str,
    is_internal: bool = False,
) -> TicketComment:
    comment = TicketComment(
        ticket_id=ticket.id,
        user_id=user.id,
        content=content.strip(),
        is_internal=is_internal,
    )
    db.session.add(comment)
    _log_activity(
        user_id=user.id,
        ticket_id=ticket.id,
        action="comment_added",
        description=f"{'Internal' if is_internal else 'Public'} comment added",
    )
    db.session.commit()
    return comment


def search_tickets(
    query: str = None,
    department_id: int = None,
    status: str = None,
    priority: str = None,
    created_by_id: int = None,
    assigned_to_id: int = None,
    page: int = 1,
    per_page: int = 20,
    date_from: str = None,
    date_to: str = None,
):
    """Advanced ticket search with multiple filters."""
    q = Ticket.query

    if query:
        q = q.filter(
            or_(
                Ticket.title.ilike(f"%{query}%"),
                Ticket.description.ilike(f"%{query}%"),
                Ticket.ticket_number.ilike(f"%{query}%"),
            )
        )
    if department_id:
        q = q.filter_by(department_id=department_id)
    if status:
        q = q.filter_by(status=status)
    if priority:
        q = q.filter_by(priority=priority)
    if created_by_id:
        q = q.filter_by(created_by_id=created_by_id)
    if assigned_to_id:
        q = q.filter_by(assigned_to_id=assigned_to_id)
    if date_from:
        q = q.filter(Ticket.created_at >= date_from)
    if date_to:
        q = q.filter(Ticket.created_at <= date_to)

    q = q.order_by(Ticket.created_at.desc())
    return q.paginate(page=page, per_page=per_page, error_out=False)


def _log_activity(
    action: str,
    description: str = None,
    user_id: int = None,
    ticket_id: int = None,
):
    try:
        log = ActivityLog(
            user_id=user_id,
            ticket_id=ticket_id,
            action=action,
            description=description,
            ip_address=flask_request.remote_addr if flask_request else None,
        )
        db.session.add(log)
    except Exception as e:
        logger.debug("Activity log error: %s", e)
