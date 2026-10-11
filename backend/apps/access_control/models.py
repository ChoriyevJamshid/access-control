from django.db import models
from django.db.models import Q, F
from apps.base_models import BaseModel
from apps.access_control.choices import AccessEventType


class AccessEvent(BaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True
    )

    timestamp = models.DateTimeField(db_index=True)

    type = models.CharField(
        max_length=31,
        choices=AccessEventType.choices,
        db_index=True
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.employee} | {self.type} | {self.timestamp}"


class WorkSession(BaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="work_sessions",
        db_index=True
    )

    started = models.DateTimeField(db_index=True)
    ended = models.DateTimeField(null=True, blank=True, db_index=True)

    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    closed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-started']
        indexes = [
            models.Index(fields=['employee', 'started']),
            models.Index(fields=['employee', 'closed']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(ended__gte=F('started')),
                name='worksession_ended_after_started'
            )
        ]

    def __str__(self):
        return f"{self.employee} | {self.started} - {self.ended}"


class DailyAttendance(BaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="daily_attendances",
        db_index=True
    )

    date = models.DateField(db_index=True)

    work_seconds = models.PositiveIntegerField(default=0)
    late_seconds = models.PositiveIntegerField(default=0)
    planned_seconds = models.PositiveIntegerField(default=0)
    overtime_seconds = models.PositiveIntegerField(default=0)
    early_leave_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['employee', 'date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_employee_daily_attendance'
            )
        ]

    def __str__(self):
        return f"{self.employee} | {self.date}"