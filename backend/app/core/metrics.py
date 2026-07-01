"""Prometheus metrics configuration and custom indicators for SecureBank."""

from prometheus_client import Counter, Gauge
from app.database import SessionLocal
from app.models import User

# Counters for business events
user_logins_total = Counter(
    "securebank_user_logins_total",
    "Total number of user login attempts",
    ["status"]  # "success" or "failed"
)

user_registrations_total = Counter(
    "securebank_user_registrations_total",
    "Total number of user registrations",
    ["status"]  # "success" or "failed"
)

# Gauges for database status (updated on scrape)
active_users_gauge = Gauge(
    "securebank_active_users",
    "Number of active users in the database"
)

inactive_users_gauge = Gauge(
    "securebank_inactive_users",
    "Number of inactive users in the database"
)


def update_user_status_metrics() -> None:
    """Query the database to count active and inactive users and update the gauges."""
    db_session = SessionLocal()
    try:
        active_count = db_session.query(User).filter(User.is_active == True).count()
        inactive_count = db_session.query(User).filter(User.is_active == False).count()
        active_users_gauge.set(active_count)
        inactive_users_gauge.set(inactive_count)
    except Exception:
        # Avoid crashing the scrape endpoint if DB query fails temporarily
        pass
    finally:
        db_session.close()
