# dashboard/services.py

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta

from apps.access_control.models import DailyAttendance
from .selectors import (
    get_total_employees,
    get_total_departments,
    get_today_attendance,
    get_7_days_activity,
)


def percent_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 2)


def percent(part, total):
    if total <= 0:
        return 0
    return round((part / total) * 100, 2)


def get_user_enterprise(user):
    try:
        return user.enterprise
    except ObjectDoesNotExist:
        return None


def build_7_days_activity_series(enterprise):
    today = timezone.localdate()
    start_date = today - timedelta(days=6)
    raw_rows = list(get_7_days_activity(enterprise))
    raw_map = {row["date"]: row for row in raw_rows}

    rows = []
    current = start_date
    while current <= today:
        row = raw_map.get(current)
        rows.append({
            "date": current,
            "present_count": row["present_count"] if row else 0,
            "total_work_seconds": row["total_work_seconds"] if row and row["total_work_seconds"] else 0,
            "total_late_seconds": row["total_late_seconds"] if row and row["total_late_seconds"] else 0,
        })
        current += timedelta(days=1)

    return rows


def get_dashboard_data(user):
    enterprise = get_user_enterprise(user)
    if not enterprise:
        raise ValueError("User is not linked to an enterprise")

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    total_employees = get_total_employees(enterprise)
    total_departments = get_total_departments(enterprise)

    today_qs = get_today_attendance(enterprise)
    yesterday_qs = DailyAttendance.objects.filter(
        employee__enterprise=enterprise,
        date=yesterday
    )

    today_present = today_qs.count()
    yesterday_present = yesterday_qs.count()

    today_late = today_qs.filter(late_seconds__gt=0).count()
    yesterday_late = yesterday_qs.filter(late_seconds__gt=0).count()

    activity_7_days = build_7_days_activity_series(enterprise)

    alerts = []
    present_change = percent_change(today_present, yesterday_present)
    late_change = percent_change(today_late, yesterday_late)
    if late_change >= 30:
        alerts.append({
            "level": "warning",
            "code": "LATE_SPIKE",
            "message": "Late arrivals increased significantly compared to yesterday",
        })
    if total_employees > 0 and percent(today_present, total_employees) < 70:
        alerts.append({
            "level": "warning",
            "code": "LOW_ATTENDANCE",
            "message": "Attendance is below 70% today",
        })

    return {
        "summary": {
            "total_employees": total_employees,
            "total_departments": total_departments,
            "today_present": today_present,
            "today_present_percent": percent(today_present, total_employees),
            "today_present_change_percent": present_change,
            "today_late": today_late,
            "today_late_percent": percent(today_late, today_present),
            "today_late_change_percent": late_change,
        },
        "series": {
            "activity_7_days": activity_7_days,
        },
        "alerts": alerts,
        "meta": {
            "as_of": today,
            "timezone": timezone.get_current_timezone_name(),
        },
    }