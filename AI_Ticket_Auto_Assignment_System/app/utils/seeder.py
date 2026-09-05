"""
Database Seeder — seeds default departments, admin user, and sample agents
"""
import logging
from ..extensions import db
from ..models.user import User
from ..models.department import Department

logger = logging.getLogger(__name__)

DEPARTMENTS_SEED = [
    {"name": "Hardware",    "code": "HW",  "icon": "bi-cpu",            "color": "#0284c7", "sla_hours": 8,  "description": "Physical hardware issues, peripherals, and equipment"},
    {"name": "Software",    "code": "SW",  "icon": "bi-code-square",    "color": "#22c55e", "sla_hours": 4,  "description": "Application issues, software installation, and updates"},
    {"name": "Network",     "code": "NET", "icon": "bi-wifi",           "color": "#3b82f6", "sla_hours": 2,  "description": "Internet, VPN, WiFi, and network connectivity issues"},
    {"name": "Database",    "code": "DB",  "icon": "bi-database",       "color": "#f59e0b", "sla_hours": 6,  "description": "Database errors, performance, backups, and administration"},
    {"name": "Cloud",       "code": "CLD", "icon": "bi-cloud",          "color": "#06b6d4", "sla_hours": 4,  "description": "Cloud infrastructure, AWS/Azure/GCP issues"},
    {"name": "Security",    "code": "SEC", "icon": "bi-shield-lock",    "color": "#ef4444", "sla_hours": 1,  "description": "Security incidents, breaches, phishing, and access issues"},
    {"name": "HR",          "code": "HR",  "icon": "bi-people",         "color": "#ec4899", "sla_hours": 24, "description": "HR portal, payroll, leave, and onboarding issues"},
    {"name": "Finance",     "code": "FIN", "icon": "bi-currency-dollar","color": "#84cc16", "sla_hours": 48, "description": "Invoices, expense reports, ERP, and financial systems"},
    {"name": "CRM Support", "code": "CRM", "icon": "bi-person-lines-fill","color": "#f97316","sla_hours": 12,"description": "CRM system, Salesforce, customer data, and sales tools"},
    {"name": "DevOps",      "code": "DEV", "icon": "bi-gear",           "color": "#8b5cf6", "sla_hours": 3,  "description": "CI/CD, deployments, infrastructure, and monitoring"},
]

SAMPLE_USERS = [
    {"first_name": "System",  "last_name": "Admin",    "email": None,                   "role": "admin",    "dept_code": None,  "is_verified": True},
    {"first_name": "Alice",   "last_name": "Johnson",  "email": "alice@company.com",    "role": "agent",    "dept_code": "HW",  "is_verified": True},
    {"first_name": "Bob",     "last_name": "Smith",    "email": "bob@company.com",      "role": "agent",    "dept_code": "NET", "is_verified": True},
    {"first_name": "Carol",   "last_name": "White",    "email": "carol@company.com",    "role": "agent",    "dept_code": "SW",  "is_verified": True},
    {"first_name": "David",   "last_name": "Brown",    "email": "david@company.com",    "role": "agent",    "dept_code": "SEC", "is_verified": True},
    {"first_name": "Emma",    "last_name": "Wilson",   "email": "emma@company.com",     "role": "employee", "dept_code": "HW",  "is_verified": True},
    {"first_name": "Frank",   "last_name": "Davis",    "email": "frank@company.com",    "role": "employee", "dept_code": "SW",  "is_verified": True},
    {"first_name": "Grace",   "last_name": "Miller",   "email": "grace@company.com",    "role": "employee", "dept_code": "FIN", "is_verified": True},
]


def seed_departments() -> dict:
    """Seed departments if they don't exist. Returns {code: department} map."""
    dept_map = {}
    for dept_data in DEPARTMENTS_SEED:
        existing = Department.query.filter_by(code=dept_data["code"]).first()
        if not existing:
            dept = Department(**dept_data)
            db.session.add(dept)
            db.session.flush()
            dept_map[dept_data["code"]] = dept
            logger.info("Created department: %s", dept_data["name"])
        else:
            dept_map[dept_data["code"]] = existing
    db.session.commit()
    return dept_map


def seed_users(dept_map: dict, admin_email: str = "admin@company.com", admin_password: str = "Admin@123456"):
    """Seed admin and sample users."""
    from flask import current_app

    admin_email = current_app.config.get("ADMIN_EMAIL", admin_email)
    admin_password = current_app.config.get("ADMIN_PASSWORD", admin_password)

    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            first_name="System",
            last_name="Admin",
            email=admin_email,
            role="admin",
            is_active=True,
            is_verified=True,
            employee_id="EMP-0001",
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        logger.info("Created admin user: %s", admin_email)

    emp_counter = 2
    for user_data in SAMPLE_USERS:
        email = user_data["email"]
        if email is None:
            continue
        if User.query.filter_by(email=email).first():
            continue

        dept_code = user_data.get("dept_code")
        dept = dept_map.get(dept_code) if dept_code else None

        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=email,
            role=user_data["role"],
            department_id=dept.id if dept else None,
            is_active=True,
            is_verified=user_data.get("is_verified", False),
            employee_id=f"EMP-{emp_counter:04d}",
        )
        user.set_password("Password@123")
        db.session.add(user)
        emp_counter += 1

    db.session.commit()
    logger.info("Users seeded successfully.")


def seed_all():
    """Run all seeders in correct order."""
    logger.info("Starting database seeding...")
    dept_map = seed_departments()
    seed_users(dept_map)
    logger.info("Database seeding complete!")
    print("[OK] Departments seeded:", len(dept_map))
    print("[OK] Users seeded successfully")
    print("\nLogin credentials:")
    print("   Admin    -> admin@company.com     / Admin@123456")
    print("   Agent    -> alice@company.com     / Password@123")
    print("   Employee -> emma@company.com      / Password@123")
