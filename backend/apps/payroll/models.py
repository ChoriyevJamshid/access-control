from django.db import models
from django.db.models import Q
from apps.base_models import BaseModel


class PayrollPeriod(BaseModel):
    start_date = models.DateField(db_index=True, blank=True, null=True)
    end_date = models.DateField(db_index=True)

    is_closed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=models.F("start_date")),
                name="payroll_period_valid_range"
            ),
            models.UniqueConstraint(
                fields=["start_date", "end_date"],
                name="unique_payroll_period"
            )
        ]

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"


class EmployeePayroll(BaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="payrolls",
        db_index=True
    )

    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name="employee_payrolls",
        db_index=True
    )

    total_work_seconds = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    calculated_at = models.DateTimeField(auto_now=True)

    is_finalized = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-period__start_date"]
        indexes = [
            models.Index(fields=["employee", "period"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "period"],
                name="unique_employee_payroll_per_period"
            )
        ]

    def __str__(self):
        return f"{self.employee} | {self.period}"


class PayrollItem(BaseModel):
    class ItemType(models.TextChoices):
        BASE = "base", "Base Salary"
        OVERTIME = "overtime", "Overtime"
        BONUS = "bonus", "Bonus"
        PENALTY = "penalty", "Penalty"
        MANUAL = "manual", "Manual Adjustment"

    payroll = models.ForeignKey(
        EmployeePayroll,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True
    )

    type = models.CharField(
        max_length=32,
        choices=ItemType.choices,
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["payroll", "type"]),
        ]

    def __str__(self):
        return f"{self.type} | {self.amount}"
