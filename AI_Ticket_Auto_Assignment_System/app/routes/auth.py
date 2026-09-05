"""
Authentication Blueprint — Login, Logout, Register
"""
from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, session
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from ..extensions import db
from ..models.user import User
from ..models.department import Department
from ..utils.helpers import get_client_ip

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Forms ─────────────────────────────────────────────────────────────────────

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(2, 50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(2, 50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    department_id = SelectField("Department", coerce=int, choices=[], validators=[DataRequired()])
    password = PasswordField("Password", validators=[
        DataRequired(), Length(8, 128,
        message="Password must be at least 8 characters")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match")
    ])
    submit = SubmitField("Create Account")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("An account with this email already exists.")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField("Confirm New Password", validators=[
        DataRequired(), EqualTo("new_password", message="Passwords must match")
    ])
    submit = SubmitField("Update Password")


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Your account has been deactivated. Contact administrator.", "danger")
                return render_template("auth/login.html", form=form)
            login_user(user, remember=form.remember.data)
            user.update_last_login()
            flash(f"Welcome back, {user.first_name}! 👋", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return _redirect_by_role(user.role)
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    name = current_user.first_name
    logout_user()
    flash(f"You have been logged out. See you soon, {name}! 👋", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    form = RegisterForm()
    departments = Department.query.filter_by(is_active=True).all()
    form.department_id.choices = [(d.id, d.name) for d in departments]

    if form.validate_on_submit():
        # Generate employee ID
        count = User.query.count()
        employee_id = f"EMP-{count + 1:04d}"

        user = User(
            first_name=form.first_name.data.strip().title(),
            last_name=form.last_name.data.strip().title(),
            email=form.email.data.lower().strip(),
            role="employee",
            department_id=form.department_id.data,
            is_active=True,
            is_verified=False,
            employee_id=employee_id,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Account created successfully! Welcome, {user.first_name}! 🎉", "success")
        return redirect(url_for("employee.dashboard"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    from ..models.ticket import Ticket
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully!", "success")

    # Build stats for profile page
    base_q = Ticket.query.filter_by(created_by_id=current_user.id)
    stats = {
        "total": base_q.count(),
        "open": base_q.filter_by(status="open").count(),
        "in_progress": base_q.filter_by(status="in_progress").count(),
        "resolved": base_q.filter(Ticket.status.in_(["resolved", "closed"])).count(),
    }
    return render_template("auth/profile.html", form=form, user=current_user, stats=stats)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _redirect_by_role(role: str):
    routes = {"admin": "admin.dashboard", "agent": "agent.dashboard", "employee": "employee.dashboard"}
    return redirect(url_for(routes.get(role, "employee.dashboard")))
