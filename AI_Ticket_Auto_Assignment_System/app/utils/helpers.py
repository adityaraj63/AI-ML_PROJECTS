"""
Utility helpers
"""
import re
import bleach
from datetime import datetime, timezone
from flask import request


def sanitize_html(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    allowed_tags = ["b", "i", "u", "em", "strong", "p", "br"]
    return bleach.clean(text, tags=allowed_tags, strip=True)


def time_ago(dt: datetime) -> str:
    """Return a human-readable time difference."""
    if dt is None:
        return "Never"
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        m = seconds // 60
        return f"{m} minute{'s' if m > 1 else ''} ago"
    elif seconds < 86400:
        h = seconds // 3600
        return f"{h} hour{'s' if h > 1 else ''} ago"
    elif seconds < 604800:
        d = seconds // 86400
        return f"{d} day{'s' if d > 1 else ''} ago"
    elif seconds < 2592000:
        w = seconds // 604800
        return f"{w} week{'s' if w > 1 else ''} ago"
    else:
        return dt.strftime("%b %d, %Y")


def format_duration(hours: float) -> str:
    """Format hours into a human-readable duration."""
    if hours is None:
        return "N/A"
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes}m"
    elif hours < 24:
        return f"{hours:.1f}h"
    else:
        days = int(hours // 24)
        remaining_h = int(hours % 24)
        return f"{days}d {remaining_h}h" if remaining_h else f"{days}d"


def validate_email(email: str) -> bool:
    """Simple email format validation."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def get_client_ip() -> str:
    """Get the real client IP address."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "unknown"


def paginate_query(query, page: int, per_page: int):
    """Helper for paginating SQLAlchemy queries."""
    return query.paginate(page=page, per_page=per_page, error_out=False)
