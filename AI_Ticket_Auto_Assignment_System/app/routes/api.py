"""
REST API Blueprint — v1
Endpoints: auth, tickets, prediction, departments, analytics, dashboard
"""
import json
from functools import wraps
from flask import Blueprint, request, jsonify, g
from flask_login import current_user, login_required

from ..extensions import db
from ..models.user import User
from ..models.ticket import Ticket
from ..models.department import Department
from ..models.prediction_log import PredictionLog
from ..services.ticket_service import create_ticket, search_tickets, update_ticket_status
from ..services.analytics_service import get_dashboard_stats, get_all_charts_data
from ..ml.predictor import get_prediction_service

api_bp = Blueprint("api", __name__)


def api_login_required(f):
    """Decorator for API routes — returns JSON 401 if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required", "code": 401}), 401
        return f(*args, **kwargs)
    return decorated


def api_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if current_user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


def success(data=None, message="Success", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status


def error(message, status=400):
    return jsonify({"success": False, "error": message}), status


# ── Auth API ───────────────────────────────────────────────────────────────────

@api_bp.route("/auth/me", methods=["GET"])
@api_login_required
def me():
    return success(current_user.to_dict())


@api_bp.route("/auth/status", methods=["GET"])
def auth_status():
    return success({
        "authenticated": current_user.is_authenticated,
        "user": current_user.to_dict() if current_user.is_authenticated else None,
    })


# ── Prediction API ─────────────────────────────────────────────────────────────

@api_bp.route("/predict", methods=["POST"])
@api_login_required
def predict():
    """
    POST /api/v1/predict
    Body: {"title": "...", "description": "..."}
    Returns prediction with confidence, priority, keywords.
    """
    data = request.get_json(silent=True)
    if not data:
        return error("Request body must be JSON")

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()

    if not title or not description:
        return error("Both 'title' and 'description' are required")
    if len(title) < 5:
        return error("Title must be at least 5 characters")
    if len(description) < 10:
        return error("Description must be at least 10 characters")

    svc = get_prediction_service()
    result = svc.predict(title, description)

    if not result["success"]:
        return error(result["message"], 503)

    return success({
        "predicted_department": result["predicted_department"],
        "confidence": result["confidence"],
        "priority": result["priority"],
        "estimated_resolution_hours": result["estimated_hours"],
        "keywords": result["keywords"],
        "all_probabilities": dict(
            sorted(result["all_probabilities"].items(), key=lambda x: x[1], reverse=True)[:5]
        ),
        "model_name": result["model_name"],
    })


@api_bp.route("/predict/similar", methods=["POST"])
@api_login_required
def predict_similar():
    """Return top 3 department candidates for a ticket."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    svc = get_prediction_service()
    similar = svc.find_similar(title, description)
    return success(similar)


# ── Tickets API ────────────────────────────────────────────────────────────────

@api_bp.route("/tickets", methods=["GET"])
@api_login_required
def list_tickets():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    status = request.args.get("status")
    priority = request.args.get("priority")
    dept_id = request.args.get("department_id", type=int)
    q = request.args.get("q")

    # Role-based filtering
    created_by_id = None
    if current_user.role == "employee":
        created_by_id = current_user.id

    pagination = search_tickets(
        query=q,
        status=status,
        priority=priority,
        department_id=dept_id,
        created_by_id=created_by_id,
        page=page,
        per_page=per_page,
    )
    return success({
        "tickets": [t.to_dict() for t in pagination.items],
        "pagination": {
            "page": pagination.page,
            "pages": pagination.pages,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        },
    })


@api_bp.route("/tickets", methods=["POST"])
@api_login_required
def create_ticket_api():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    priority = data.get("priority", "medium")

    if not title or len(title) < 5:
        return error("Valid title required (min 5 chars)")
    if not description or len(description) < 20:
        return error("Valid description required (min 20 chars)")
    if priority not in ("low", "medium", "high", "critical"):
        return error("Priority must be one of: low, medium, high, critical")

    ticket, prediction = create_ticket(title, description, priority, current_user, run_ai=True)
    response = ticket.to_dict()
    if prediction:
        response["ai_prediction"] = {
            "department": prediction.get("predicted_department"),
            "confidence": prediction.get("confidence"),
            "priority": prediction.get("priority"),
            "keywords": prediction.get("keywords"),
        }
    return success(response, "Ticket created successfully", 201)


@api_bp.route("/tickets/<int:ticket_id>", methods=["GET"])
@api_login_required
def get_ticket_api(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return error("Ticket not found", 404)
    if current_user.role == "employee" and ticket.created_by_id != current_user.id:
        return error("Access denied", 403)
    return success(ticket.to_dict())


@api_bp.route("/tickets/<int:ticket_id>/status", methods=["PATCH"])
@api_login_required
def update_status_api(ticket_id: int):
    if current_user.role == "employee":
        return error("Permission denied", 403)
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return error("Ticket not found", 404)
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    valid_statuses = ["open", "in_progress", "resolved", "closed", "escalated"]
    if new_status not in valid_statuses:
        return error(f"Status must be one of: {', '.join(valid_statuses)}")
    update_ticket_status(ticket, new_status, current_user, data.get("notes"))
    return success(ticket.to_dict(), "Status updated")


# ── Departments API ────────────────────────────────────────────────────────────

@api_bp.route("/departments", methods=["GET"])
@api_login_required
def list_departments():
    depts = Department.query.filter_by(is_active=True).all()
    return success([d.to_dict() for d in depts])


# ── Analytics API ──────────────────────────────────────────────────────────────

@api_bp.route("/analytics/dashboard", methods=["GET"])
@api_admin_required
def analytics_dashboard():
    stats = get_dashboard_stats()
    return success(stats)


@api_bp.route("/analytics/charts", methods=["GET"])
@api_admin_required
def analytics_charts():
    charts = get_all_charts_data()
    return success(charts)


# ── ML Model API ───────────────────────────────────────────────────────────────

@api_bp.route("/ml/status", methods=["GET"])
@api_login_required
def ml_status():
    svc = get_prediction_service()
    return success({
        "model_loaded": svc.is_model_loaded,
        "model_name": svc.model_name,
        "labels": svc.labels,
        "metrics": svc.best_metrics,
    })


# ── Users API ──────────────────────────────────────────────────────────────────

@api_bp.route("/users", methods=["GET"])
@api_admin_required
def list_users():
    users = User.query.filter_by(is_active=True).all()
    return success([u.to_dict() for u in users])


@api_bp.route("/users/agents", methods=["GET"])
@api_login_required
def list_agents():
    agents = User.query.filter_by(role="agent", is_active=True).all()
    return success([u.to_dict() for u in agents])
