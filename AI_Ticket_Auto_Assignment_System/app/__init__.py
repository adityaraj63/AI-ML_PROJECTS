"""
Flask Application Factory
"""
import os
import logging
from flask import Flask
from .config import config_map
from .extensions import db, login_manager, csrf, migrate, cors


def create_app(env: str = None) -> Flask:
    """Create and configure the Flask application."""

    env = env or os.environ.get("FLASK_ENV", "development")
    config_class = config_map.get(env, config_map["default"])

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # ── Extensions ──────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # ── Logging ─────────────────────────────────────────────────────────────
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Blueprints ───────────────────────────────────────────────────────────
    from .routes.auth import auth_bp
    from .routes.employee import employee_bp
    from .routes.admin import admin_bp
    from .routes.agent import agent_bp
    from .routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp, url_prefix="/employee")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(agent_bp, url_prefix="/agent")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # ── User loader ──────────────────────────────────────────────────────────
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Root redirect ────────────────────────────────────────────────────────
    from flask import redirect, url_for
    from flask_login import current_user

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            role = current_user.role
            if role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif role == "agent":
                return redirect(url_for("agent.dashboard"))
            else:
                return redirect(url_for("employee.dashboard"))
        return redirect(url_for("auth.login"))

    # ── Error handlers ───────────────────────────────────────────────────────
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # ── Context processors ───────────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        from .models.ticket import Ticket
        from .models.department import Department
        from .extensions import db as _db
        from sqlalchemy import text as sql_text

        ctx = {"db": _db}
        try:
            ctx["total_tickets"] = Ticket.query.count()
            ctx["departments"] = Department.query.filter_by(is_active=True).all()
        except Exception:
            ctx["total_tickets"] = 0
            ctx["departments"] = []
        return ctx

    return app
