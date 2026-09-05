"""
Decorators — role-based access control
"""
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """Decorator that restricts access to specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    """Shortcut for admin-only routes."""
    return role_required("admin")(f)


def agent_or_admin_required(f):
    """Shortcut for agent or admin routes."""
    return role_required("agent", "admin")(f)


def active_user_required(f):
    """Ensure user account is active."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated and not current_user.is_active:
            flash("Your account has been deactivated. Contact admin.", "danger")
            return redirect(url_for("auth.logout"))
        return f(*args, **kwargs)
    return decorated
