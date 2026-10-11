# dashboard/selectors.py

from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta

from apps.employees.models import Employee
from apps.users.models import Department
from apps.access_control.models import DailyAttendance


def get_total_employees(enterprise):
    return Employee.objects.filter(
        enterprise=enterprise
    ).count()


def get_total_departments(enterprise):
    return Department.objects.filter(
        enterprise=enterprise, parent__isnull=True
    ).count()


def get_today_attendance(enterprise):
    today = timezone.localdate()

    return DailyAttendance.objects.filter(
        employee__enterprise=enterprise,
        date=today
    )


def get_7_days_activity(enterprise):
    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    return (
        DailyAttendance.objects
        .filter(
            employee__enterprise=enterprise,
            date__range=[start_date, today]
        )
        .values("date")
        .annotate(
            present_count=Count("employee", distinct=True),
            total_work_seconds=Sum("work_seconds"),
            total_late_seconds=Sum("late_seconds"),
        )
        .order_by("date")
    )