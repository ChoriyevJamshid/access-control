from celery import shared_task
from django.db import transaction

from apps.access_control.choices import AccessEventType
from apps.access_control.services import _update_daily_attendance
from apps.access_control.models import AccessEvent, WorkSession


@shared_task(bind=True, max_retries=3)
def processing_work_session(self, access_event_id: int):
    try:
        with transaction.atomic():

            access_event = (
                AccessEvent.objects
                .select_related("employee")
                .filter(id=access_event_id)
                .first()
            )

            if not access_event:
                return

            employee = access_event.employee

            employee_detail = (
                employee.details
                .filter(is_active=True)
                .prefetch_related("work_days")
                .first()
            )

            if not employee_detail:
                return

            # 🔹 Проверка рабочего дня
            current_weekday = access_event.timestamp.weekday()

            work_day = employee_detail.work_days.filter(
                weekday=current_weekday
            ).first()

            if not work_day:
                return

            # =========================================================
            # 🔹 ENTER
            # =========================================================
            if access_event.type == AccessEventType.ENTER:

                open_session = (
                    WorkSession.objects
                    .select_for_update()
                    .filter(
                        employee=employee,
                        closed=False
                    )
                    .order_by("-started")
                    .first()
                )

                # если есть открытая — закрываем
                if open_session:
                    if open_session.started <= access_event.timestamp:
                        open_session.ended = access_event.timestamp
                        duration = (open_session.ended - open_session.started).total_seconds()
                        open_session.duration_seconds = int(duration)

                    open_session.closed = True
                    open_session.save(
                        update_fields=[
                            "ended",
                            "duration_seconds",
                            "closed",
                        ]
                    )

                    if open_session.ended and open_session.duration_seconds:
                        _update_daily_attendance(open_session)

                WorkSession.objects.create(
                    employee=employee,
                    started=access_event.timestamp,
                    closed=False
                )

                return

            # =========================================================
            # 🔹 LEAVE
            # =========================================================
            work_session = (
                WorkSession.objects
                .select_for_update()
                .filter(
                    employee=employee,
                    closed=False
                )
                .order_by("-started")
                .first()
            )

            if not work_session:
                return

            if work_session.started > access_event.timestamp:
                return

            work_session.ended = access_event.timestamp

            duration = (
                work_session.ended - work_session.started
            ).total_seconds()

            work_session.duration_seconds = int(duration)
            work_session.closed = True

            work_session.save(
                update_fields=[
                    "ended",
                    "duration_seconds",
                    "closed",
                ]
            )

            # 🔹 Обновляем DailyAttendance
            _update_daily_attendance(work_session)

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
