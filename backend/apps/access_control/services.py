from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.access_control.models import AccessEvent, DailyAttendance, WorkSession


def check_access_exists_service(employee, timestamp, event_type):

    return AccessEvent.objects.filter(employee=employee,
                                      timestamp=timestamp,
                                      type=event_type).exists()


def _update_daily_attendance(work_session):
    if not work_session.closed or not work_session.duration_seconds:
        return

    employee = work_session.employee

    local_start = timezone.localtime(work_session.started)
    local_end = timezone.localtime(work_session.ended)

    work_date = local_start.date()
    weekday = local_start.weekday()

    employee_detail = (
        employee.details
        .filter(is_active=True)
        .prefetch_related("work_days")
        .first()
    )

    planned_seconds = 0
    late_seconds = 0
    early_leave_seconds = 0
    overtime_seconds = 0

    # Rebuild whole day from closed sessions to avoid inflating late/early
    # when an employee has multiple sessions in one day.
    day_sessions = list(
        WorkSession.objects
        .filter(
            employee=employee,
            closed=True,
            ended__isnull=False,
            started__date=work_date,
        )
        .order_by("started")
    )

    if not day_sessions:
        return

    total_work_seconds = sum(int(item.duration_seconds or 0) for item in day_sessions)

    first_start = timezone.localtime(day_sessions[0].started)
    last_end = timezone.localtime(day_sessions[-1].ended)

    if employee_detail:
        work_day = employee_detail.work_days.filter(
            weekday=weekday
        ).first()

        if work_day:
            planned_seconds = int(work_day.hours.total_seconds())

            # собираем datetime для плана
            planned_start = timezone.make_aware(
                datetime.combine(work_date, work_day.from_time)
            )

            planned_end = timezone.make_aware(
                datetime.combine(work_date, work_day.to_time)
            )

            # --- LATE ---
            if first_start > planned_start:
                late_seconds = int((first_start - planned_start).total_seconds())

            # --- EARLY LEAVE ---
            if last_end < planned_end:
                early_leave_seconds = int((planned_end - last_end).total_seconds())

            # --- OVERTIME ---
            if last_end > planned_end:
                overtime_seconds = int((last_end - planned_end).total_seconds())

    with transaction.atomic():
        DailyAttendance.objects.update_or_create(
            employee=employee,
            date=work_date,
            defaults={
                "work_seconds": total_work_seconds,
                "late_seconds": late_seconds,
                "planned_seconds": planned_seconds,
                "overtime_seconds": overtime_seconds,
                "early_leave_seconds": early_leave_seconds,
            }
        )