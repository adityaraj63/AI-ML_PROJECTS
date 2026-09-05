"""
Admin Blueprint — Full admin dashboard, user management, ticket management, analytics
"""
import json
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, abort, jsonify
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, TextAreaField,
                     BooleanField, SubmitField, IntegerField)
from wtforms.validators import DataRequired, Email, Length, NumberRange

from ..extensions import db
from ..models.user import User
from ..models.ticket import Ticket
from ..models.department import Department
from ..models.prediction_log import PredictionLog, ActivityLog
from ..services.ticket_service import (
    update_ticket_status, assign_ticket,
    correct_ai_prediction, add_comment, search_tickets
)
from ..services.analytics_service import (
    get_dashboard_stats, get_all_charts_data,
    get_department_workload, get_agent_performance,
    get_recent_activity
)
from ..utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


# ── Forms ──────────────────────────────────────────────────────────────────────

class UserForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(2, 50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(2, 50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = SelectField("Role", choices=[("employee", "Employee"), ("agent", "Support Agent"), ("admin", "Administrator")])
    department_id = SelectField("Department", coerce=int, choices=[])
    is_active = BooleanField("Active")
    submit = SubmitField("Save User")


class DepartmentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(2, 100)])
    code = StringField("Code", validators=[DataRequired(), Length(2, 20)])
    description = TextAreaField("Description")
    email = StringField("Email")
    icon = StringField("Bootstrap Icon Class", default="bi-building")
    color = StringField("Color (Hex)", default="#6366f1")
    sla_hours = IntegerField("SLA Hours", default=24, validators=[NumberRange(1, 720)])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Department")


class TicketUpdateForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("open", "Open"), ("in_progress", "In Progress"),
        ("resolved", "Resolved"), ("closed", "Closed"), ("escalated", "Escalated")
    ])
    priority = SelectField("Priority", choices=[
        ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")
    ])
    assigned_to_id = SelectField("Assign To", coerce=int, choices=[])
    department_id = SelectField("Department", coerce=int, choices=[])
    resolution_notes = TextAreaField("Resolution Notes")
    comment = TextAreaField("Internal Comment")
    submit = SubmitField("Update Ticket")


# ── Dashboard ──────────────────────────────────────────────────────────────────

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = get_dashboard_stats()
    dept_workload = get_department_workload()
    agent_perf = get_agent_performance()
    recent_activity = get_recent_activity(10)
    charts_data = get_all_charts_data()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        dept_workload=dept_workload,
        agent_perf=agent_perf,
        recent_activity=recent_activity,
        charts_data=json.dumps(charts_data),
    )


# ── Tickets ────────────────────────────────────────────────────────────────────

@admin_bp.route("/tickets")
@login_required
@admin_required
def tickets():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    dept_id = request.args.get("dept_id", None, type=int)
    q = request.args.get("q", "")

    pagination = search_tickets(
        query=q or None,
        status=status or None,
        priority=priority or None,
        department_id=dept_id,
        page=page,
        per_page=20,
    )
    departments = Department.query.filter_by(is_active=True).all()
    return render_template(
        "admin/tickets.html",
        pagination=pagination,
        departments=departments,
        status=status,
        priority=priority,
        dept_id=dept_id,
        query=q,
    )


@admin_bp.route("/tickets/<int:ticket_id>", methods=["GET", "POST"])
@login_required
@admin_required
def ticket_detail(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    agents = User.query.filter_by(role="agent", is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()

    form = TicketUpdateForm()
    form.assigned_to_id.choices = [(0, "Unassigned")] + [(a.id, a.full_name) for a in agents]
    form.department_id.choices = [(0, "Unknown")] + [(d.id, d.name) for d in departments]

    if form.validate_on_submit():
        if form.status.data:
            update_ticket_status(ticket, form.status.data, current_user, form.resolution_notes.data)
        if form.assigned_to_id.data and form.assigned_to_id.data != 0:
            assign_ticket(ticket, form.assigned_to_id.data, current_user)
        if form.department_id.data and form.department_id.data != 0:
            ticket.department_id = form.department_id.data
            db.session.commit()
        if form.comment.data:
            add_comment(ticket, current_user, form.comment.data, is_internal=True)
        flash("Ticket updated successfully.", "success")
        return redirect(url_for("admin.ticket_detail", ticket_id=ticket_id))

    # Pre-fill form
    form.status.data = ticket.status
    form.priority.data = ticket.priority
    form.assigned_to_id.data = ticket.assigned_to_id or 0
    form.department_id.data = ticket.department_id or 0

    keywords, all_probs = [], {}
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
        "admin/ticket_detail.html",
        ticket=ticket,
        form=form,
        keywords=keywords,
        all_probs=all_probs,
        pred_log=pred_log,
    )


@admin_bp.route("/tickets/<int:ticket_id>/correct-prediction", methods=["POST"])
@login_required
@admin_required
def correct_prediction(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)
    correct_dept = request.form.get("correct_department")
    if correct_dept:
        correct_ai_prediction(ticket, correct_dept, current_user)
        flash(f"AI prediction corrected to {correct_dept}.", "success")
    return redirect(url_for("admin.ticket_detail", ticket_id=ticket_id))


# ── Users ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    role = request.args.get("role", "")
    q = request.args.get("q", "")

    query = User.query
    if role:
        query = query.filter_by(role=role)
    if q:
        from sqlalchemy import or_
        query = query.filter(
            or_(User.first_name.ilike(f"%{q}%"), User.last_name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
        )
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/users.html", pagination=pagination, role=role, query=q)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_user():
    form = UserForm()
    departments = Department.query.filter_by(is_active=True).all()
    form.department_id.choices = [(0, "None")] + [(d.id, d.name) for d in departments]

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email already exists.", "danger")
        else:
            count = User.query.count()
            user = User(
                first_name=form.first_name.data.strip().title(),
                last_name=form.last_name.data.strip().title(),
                email=form.email.data.lower().strip(),
                role=form.role.data,
                department_id=form.department_id.data if form.department_id.data != 0 else None,
                is_active=form.is_active.data,
                is_verified=True,
                employee_id=f"EMP-{count + 1:04d}",
            )
            user.set_password("Password@123")
            db.session.add(user)
            db.session.commit()
            flash(f"User {user.full_name} created. Default password: Password@123", "success")
            return redirect(url_for("admin.users"))

    form.is_active.data = True
    return render_template("admin/user_form.html", form=form, title="New User")


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    form = UserForm(obj=user)
    departments = Department.query.filter_by(is_active=True).all()
    form.department_id.choices = [(0, "None")] + [(d.id, d.name) for d in departments]

    if form.validate_on_submit():
        user.first_name = form.first_name.data.strip().title()
        user.last_name = form.last_name.data.strip().title()
        user.email = form.email.data.lower().strip()
        user.role = form.role.data
        user.department_id = form.department_id.data if form.department_id.data != 0 else None
        user.is_active = form.is_active.data
        db.session.commit()
        flash(f"User {user.full_name} updated.", "success")
        return redirect(url_for("admin.users"))

    form.department_id.data = user.department_id or 0
    return render_template("admin/user_form.html", form=form, title="Edit User", user=user)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = "activated" if user.is_active else "deactivated"
        flash(f"User {user.full_name} {status}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
@admin_required
def reset_user_password(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    user.set_password("Password@123")
    db.session.commit()
    flash(f"Password for {user.full_name} reset to: Password@123", "success")
    return redirect(url_for("admin.users"))


# ── Departments ────────────────────────────────────────────────────────────────

@admin_bp.route("/departments")
@login_required
@admin_required
def departments():
    depts = Department.query.order_by(Department.name).all()
    return render_template("admin/departments.html", departments=depts)


@admin_bp.route("/departments/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        dept = Department(
            name=form.name.data.strip(),
            code=form.code.data.strip().upper(),
            description=form.description.data,
            email=form.email.data,
            icon=form.icon.data or "bi-building",
            color=form.color.data or "#6366f1",
            sla_hours=form.sla_hours.data,
            is_active=form.is_active.data,
        )
        db.session.add(dept)
        db.session.commit()
        flash(f"Department '{dept.name}' created.", "success")
        return redirect(url_for("admin.departments"))
    return render_template("admin/dept_form.html", form=form, title="New Department")


@admin_bp.route("/departments/<int:dept_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_department(dept_id: int):
    dept = db.session.get(Department, dept_id)
    if not dept:
        abort(404)
    form = DepartmentForm(obj=dept)
    if form.validate_on_submit():
        dept.name = form.name.data.strip()
        dept.code = form.code.data.strip().upper()
        dept.description = form.description.data
        dept.email = form.email.data
        dept.icon = form.icon.data or "bi-building"
        dept.color = form.color.data or "#6366f1"
        dept.sla_hours = form.sla_hours.data
        dept.is_active = form.is_active.data
        db.session.commit()
        flash(f"Department '{dept.name}' updated.", "success")
        return redirect(url_for("admin.departments"))
    return render_template("admin/dept_form.html", form=form, title="Edit Department", dept=dept)


# ── Analytics ──────────────────────────────────────────────────────────────────

@admin_bp.route("/analytics")
@login_required
@admin_required
def analytics():
    stats = get_dashboard_stats()
    dept_workload = get_department_workload()
    agent_perf = get_agent_performance()
    charts_data = get_all_charts_data()

    # ML model metrics
    ml_metrics = {}
    try:
        from ..ml.predictor import get_prediction_service
        svc = get_prediction_service()
        ml_metrics = svc.all_metrics
    except Exception:
        pass

    total_predictions = PredictionLog.query.count()
    correct_predictions = PredictionLog.query.filter_by(is_correct=True).count()
    feedback_count = PredictionLog.query.filter(PredictionLog.is_correct.isnot(None)).count()
    accuracy = round(correct_predictions / feedback_count * 100, 1) if feedback_count > 0 else None

    return render_template(
        "admin/analytics.html",
        stats=stats,
        dept_workload=dept_workload,
        agent_perf=agent_perf,
        charts_data=json.dumps(charts_data),
        ml_metrics=ml_metrics,
        total_predictions=total_predictions,
        correct_predictions=correct_predictions,
        feedback_count=feedback_count,
        accuracy=accuracy,
    )


# ── ML Management ──────────────────────────────────────────────────────────────

@admin_bp.route("/ml/train", methods=["POST"])
@login_required
@admin_required
def trigger_training():
    """Trigger model retraining (async in production; synchronous here)."""
    try:
        from ..ml.dataset_generator import generate_and_save_dataset
        from ..ml.trainer import train_and_save_best_model
        from ..ml.predictor import get_prediction_service
        generate_and_save_dataset()
        result = train_and_save_best_model()
        get_prediction_service().reload()
        flash(
            f"✅ Model retrained! Best: {result['best_model_name']} | "
            f"Accuracy: {result['best_metrics'].get('accuracy', 0):.2%}",
            "success",
        )
    except Exception as e:
        flash(f"Training failed: {str(e)}", "danger")
    return redirect(url_for("admin.analytics"))


# ── Activity Logs ──────────────────────────────────────────────────────────────

@admin_bp.route("/activity")
@login_required
@admin_required
def activity_logs():
    page = request.args.get("page", 1, type=int)
    logs = (
        ActivityLog.query
        .order_by(ActivityLog.created_at.desc())
        .paginate(page=page, per_page=30, error_out=False)
    )
    return render_template("admin/activity_logs.html", pagination=logs)
