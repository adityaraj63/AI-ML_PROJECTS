"""
Agent (Support Agent / Supervisor) Blueprint
"""
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

from ..extensions import db
from ..models.ticket import Ticket
from ..models.user import User
from ..models.department import Department
from ..services.ticket_service import (
    update_ticket_status, add_comment, search_tickets, get_ticket_by_id
)
from ..utils.decorators import agent_or_admin_required

agent_bp = Blueprint("agent", __name__)


class AgentTicketForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("open", "Open"), ("in_progress", "In Progress"),
        ("resolved", "Resolved"), ("escalated", "Escalated"), ("closed", "Closed")
    ])
    comment = TextAreaField("Comment / Resolution Notes", validators=[DataRequired()])
    is_internal = SelectField("Comment Type", choices=[("0", "Public"), ("1", "Internal Only")])
    submit = SubmitField("Update")


@agent_bp.route("/dashboard")
@login_required
@agent_or_admin_required
def dashboard():
    assigned = Ticket.query.filter_by(assigned_to_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    stats = {
        "total": len(assigned),
        "open": sum(1 for t in assigned if t.status == "open"),
        "in_progress": sum(1 for t in assigned if t.status == "in_progress"),
        "resolved": sum(1 for t in assigned if t.status == "resolved"),
        "escalated": sum(1 for t in assigned if t.status == "escalated"),
    }
    # Department's tickets if agent has a dept
    dept_tickets = []
    if current_user.department_id:
        dept_tickets = (
            Ticket.query
            .filter_by(department_id=current_user.department_id)
            .order_by(Ticket.created_at.desc())
            .limit(10)
            .all()
        )
    return render_template(
        "agent/dashboard.html",
        assigned_tickets=assigned[:10],
        stats=stats,
        dept_tickets=dept_tickets,
    )


@agent_bp.route("/tickets")
@login_required
@agent_or_admin_required
def tickets():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    view = request.args.get("view", "assigned")  # assigned | department | all

    if view == "assigned":
        pagination = search_tickets(
            status=status or None,
            priority=priority or None,
            assigned_to_id=current_user.id,
            page=page,
            per_page=20,
        )
    elif view == "department" and current_user.department_id:
        pagination = search_tickets(
            status=status or None,
            priority=priority or None,
            department_id=current_user.department_id,
            page=page,
            per_page=20,
        )
    else:
        pagination = search_tickets(
            status=status or None,
            priority=priority or None,
            page=page,
            per_page=20,
        )

    return render_template(
        "agent/tickets.html",
        pagination=pagination,
        status=status,
        priority=priority,
        view=view,
    )


@agent_bp.route("/tickets/<int:ticket_id>", methods=["GET", "POST"])
@login_required
@agent_or_admin_required
def ticket_detail(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)

    form = AgentTicketForm()
    if form.validate_on_submit():
        if form.status.data != ticket.status:
            update_ticket_status(ticket, form.status.data, current_user)
        if form.comment.data:
            is_internal = form.is_internal.data == "1"
            add_comment(ticket, current_user, form.comment.data, is_internal=is_internal)
        flash("Ticket updated successfully.", "success")
        return redirect(url_for("agent.ticket_detail", ticket_id=ticket_id))

    form.status.data = ticket.status

    keywords = []
    all_probs = {}
    if ticket.ai_keywords:
        try:
            keywords = json.loads(ticket.ai_keywords)
        except Exception:
            pass
    pred_log = ticket.prediction_logs.order_by(db.text("created_at desc")).first()
    if pred_log and pred_log.all_probabilities:
        try:
            all_probs = dict(sorted(json.loads(pred_log.all_probabilities).items(), key=lambda x: x[1], reverse=True)[:5])
        except Exception:
            pass

    return render_template(
        "agent/ticket_detail.html",
        ticket=ticket,
        form=form,
        keywords=keywords,
        all_probs=all_probs,
    )


@agent_bp.route("/tickets/<int:ticket_id>/escalate", methods=["POST"])
@login_required
@agent_or_admin_required
def escalate_ticket(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)
    reason = request.form.get("reason", "Escalated by agent")
    update_ticket_status(ticket, "escalated", current_user, reason)
    flash("Ticket escalated successfully.", "warning")
    return redirect(url_for("agent.ticket_detail", ticket_id=ticket_id))


@agent_bp.route("/profile")
@login_required
@agent_or_admin_required
def profile():
    assigned = Ticket.query.filter_by(assigned_to_id=current_user.id).all()
    stats = {
        "total": len(assigned),
        "resolved": sum(1 for t in assigned if t.status == "resolved"),
        "in_progress": sum(1 for t in assigned if t.status == "in_progress"),
    }
    resolution_rate = round(stats["resolved"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
    return render_template(
        "agent/profile.html",
        user=current_user,
        stats=stats,
        resolution_rate=resolution_rate,
    )
