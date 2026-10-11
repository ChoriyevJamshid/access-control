from django.db import models
from django.db.models import Q, F
from apps.base_models import BaseModel
from apps.employees.choices import SalaryType


class Employee(BaseModel):
    enterprise = models.ForeignKey(
        "users.Enterprise",
        on_delete=models.CASCADE,
        related_name="employees",
        db_index=True,
        blank=True,
        null=True
    )

    department = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        db_index=True)

    first_name = models.CharField(max_length=31, db_index=True)
    last_name = models.CharField(max_length=31, db_index=True)
    middle_name = models.CharField(max_length=31, db_index=True)

    code = models.CharField(max_length=63)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["enterprise", "code"],
                name="unique_employee_code_per_enterprise"
            )
        ]


    @property
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        if self.middle_name:
            full_name = f"{full_name} {self.middle_name}"
        return full_name

    def save(self, *args, **kwargs):
        if self.department:
            self.enterprise = self.department.enterprise
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class EmployeeDetail(BaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="details",
        db_index=True
    )

    salary_type = models.CharField(
        max_length=20,
        choices=SalaryType.choices,
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(null=True, blank=True, db_index=True)

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-effective_from"]
        indexes = [
            models.Index(fields=["employee", "effective_from"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(effective_to__gte=F("effective_from")) | Q(effective_to__isnull=True),
                name="valid_compensation_period"
            ),
            models.UniqueConstraint(
                fields=["employee"],
                condition=Q(is_active=True),
                name="unique_active_compensation"
            )
        ]

    def __str__(self):
        return f"{self.employee} | {self.salary_type} | {self.amount}"


class EmployeeWorkDay(BaseModel):
    detail = models.ForeignKey(
        EmployeeDetail,
        on_delete=models.CASCADE,
        related_name="work_days",
        db_index=True
    )

    # Лучше integer 0-6 (Monday=0)
    weekday = models.PositiveSmallIntegerField(
        db_index=True
    )

    from_time = models.TimeField()
    to_time = models.TimeField()

    hours = models.DurationField(
        help_text="Planned work hours"
    )

    class Meta:
        ordering = ["weekday"]
        indexes = [
            models.Index(fields=["detail", "weekday"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["detail", "weekday"],
                name="unique_workday_per_detail"
            ),
            models.CheckConstraint(
                check=models.Q(to_time__gt=models.F("from_time")),
                name="valid_workday_time_range"
            )
        ]


    def __str__(self):
        return f"{self.detail_id} | {self.weekday}"
