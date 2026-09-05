"""
Employee Blueprint — Dashboard, Create Ticket, View Tickets, History
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from ..extensions import db
from ..models.ticket import Ticket
from ..models.department import Department
from ..services.ticket_service import (
    create_ticket, get_ticket_by_id, add_comment, search_tickets
)
from ..utils.decorators import active_user_required

employee_bp = Blueprint("employee", __name__)


# ── Forms ─────────────────────────────────────────────────────────────────────

class TicketForm(FlaskForm):
    title = StringField("Ticket Title", validators=[DataRequired(), Length(5, 255)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(20, 5000)])
    priority = SelectField(
        "Priority",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        default="medium",
    )
    submit = SubmitField("Submit Ticket")


class CommentForm(FlaskForm):
    content = TextAreaField("Add Comment", validators=[DataRequired(), Length(1, 2000)])
    submit = SubmitField("Post Comment")


# ── Routes ────────────────────────────────────────────────────────────────────

@employee_bp.route("/dashboard")
@login_required
@active_user_required
def dashboard():
    my_tickets = (
        Ticket.query
        .filter_by(created_by_id=current_user.id)
        .order_by(Ticket.created_at.desc())
        .limit(5)
        .all()
    )
    stats = {
        "total": Ticket.query.filter_by(created_by_id=current_user.id).count(),
        "open": Ticket.query.filter_by(created_by_id=current_user.id, status="open").count(),
        "in_progress": Ticket.query.filter_by(created_by_id=current_user.id, status="in_progress").count(),
        "resolved": Ticket.query.filter_by(created_by_id=current_user.id, status="resolved").count(),
    }
    return render_template("employee/dashboard.html", tickets=my_tickets, stats=stats)


@employee_bp.route("/tickets/new", methods=["GET", "POST"])
@login_required
@active_user_required
def new_ticket():
    form = TicketForm()
    prediction_result = None
    ticket = None

    if form.validate_on_submit():
        ticket, prediction_result = create_ticket(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            created_by=current_user,
            run_ai=True,
        )
        flash(f"Ticket {ticket.ticket_number} submitted successfully! 🎉", "success")
        return redirect(url_for("employee.ticket_detail", ticket_id=ticket.id))

    return render_template(
        "employee/new_ticket.html",
        form=form,
        prediction_result=prediction_result,
        ticket=ticket,
    )


@employee_bp.route("/tickets")
@login_required
@active_user_required
def my_tickets():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    query = request.args.get("q", "")

    pagination = search_tickets(
        query=query or None,
        status=status or None,
        priority=priority or None,
        created_by_id=current_user.id,
        page=page,
        per_page=15,
    )
    return render_template(
        "employee/my_tickets.html",
        pagination=pagination,
        status=status,
        priority=priority,
        query=query,
    )


@employee_bp.route("/tickets/<int:ticket_id>")
@login_required
@active_user_required
def ticket_detail(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)
    # Employees can only see their own tickets
    if current_user.role == "employee" and ticket.created_by_id != current_user.id:
        abort(403)

    form = CommentForm()
    import json
    keywords = []
    if ticket.ai_keywords:
        try:
            keywords = json.loads(ticket.ai_keywords)
        except Exception:
            pass

    all_probs = {}
    pred_log = ticket.prediction_logs.order_by(db.text("created_at desc")).first()
    if pred_log and pred_log.all_probabilities:
        try:
            all_probs = json.loads(pred_log.all_probabilities)
            # Sort by value desc
            all_probs = dict(sorted(all_probs.items(), key=lambda x: x[1], reverse=True)[:5])
        except Exception:
            pass

    return render_template(
        "employee/ticket_detail.html",
        ticket=ticket,
        form=form,
        keywords=keywords,
        all_probs=all_probs,
    )


@employee_bp.route("/tickets/<int:ticket_id>/comment", methods=["POST"])
@login_required
@active_user_required
def add_ticket_comment(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)
    if current_user.role == "employee" and ticket.created_by_id != current_user.id:
        abort(403)

    form = CommentForm()
    if form.validate_on_submit():
        add_comment(ticket, current_user, form.content.data)
        flash("Comment posted successfully.", "success")
    return redirect(url_for("employee.ticket_detail", ticket_id=ticket_id))


@employee_bp.route("/profile")
@login_required
def profile():
    my_tickets = Ticket.query.filter_by(created_by_id=current_user.id).all()
    stats = {
        "total": len(my_tickets),
        "open": sum(1 for t in my_tickets if t.status == "open"),
        "resolved": sum(1 for t in my_tickets if t.status == "resolved"),
    }
    return render_template("employee/profile.html", user=current_user, stats=stats)
