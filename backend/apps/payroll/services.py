from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from apps.access_control.models import DailyAttendance
from apps.employees.choices import SalaryType
from apps.payroll.models import EmployeePayroll, PayrollItem


OVERTIME_MULTIPLIER = Decimal("1.0")


def _safe_decimal(value):
    if value is None:
        return Decimal("0")
    return Decimal(value)


def _seconds_to_hours(seconds: int) -> Decimal:
    if not seconds:
        return Decimal("0")
    return Decimal(seconds) / Decimal("3600")


def _get_active_detail(employee):
    return (
        employee.details
        .filter(is_active=True)
        .first()
    )


def _get_attendance_totals(employee, period):
    qs = DailyAttendance.objects.filter(
        employee=employee,
        date__range=(period.start_date, period.end_date),
    )

    return qs.aggregate(
        total_work_seconds=Coalesce(Sum("work_seconds"), Value(0)),
        total_planned_seconds=Coalesce(Sum("planned_seconds"), Value(0)),
        total_overtime_seconds=Coalesce(Sum("overtime_seconds"), Value(0)),
        total_late_seconds=Coalesce(Sum("late_seconds"), Value(0)),
        total_early_leave_seconds=Coalesce(Sum("early_leave_seconds"), Value(0)),
    )


def _build_payroll_items(employee_detail, totals):
    work_seconds = int(totals.get("total_work_seconds") or 0)
    planned_seconds = int(totals.get("total_planned_seconds") or 0)
    overtime_seconds = int(totals.get("total_overtime_seconds") or 0)
    penalty_seconds = int(totals.get("total_late_seconds") or 0) + int(
        totals.get("total_early_leave_seconds") or 0
    )

    amount = _safe_decimal(employee_detail.amount)

    base_amount = Decimal("0")
    overtime_amount = Decimal("0")
    penalty_amount = Decimal("0")

    if employee_detail.salary_type == SalaryType.HOURLY:
        hourly_rate = amount
        base_amount = _seconds_to_hours(work_seconds) * hourly_rate
        overtime_amount = _seconds_to_hours(overtime_seconds) * hourly_rate * OVERTIME_MULTIPLIER
        penalty_amount = _seconds_to_hours(penalty_seconds) * hourly_rate
    else:
        # For monthly salary, base amount is fixed monthly amount.
        base_amount = amount

        if planned_seconds > 0:
            hourly_rate = amount / _seconds_to_hours(planned_seconds)
            overtime_amount = _seconds_to_hours(overtime_seconds) * hourly_rate * OVERTIME_MULTIPLIER
            penalty_amount = _seconds_to_hours(penalty_seconds) * hourly_rate

    return {
        "work_seconds": work_seconds,
        "base_amount": base_amount.quantize(Decimal("0.01")),
        "overtime_amount": overtime_amount.quantize(Decimal("0.01")),
        "penalty_amount": penalty_amount.quantize(Decimal("0.01")),
    }


def calculate_employee_payroll(employee, period, *, force_recalculate=False):
    print(f"{employee = }")
    if not period.start_date or not period.end_date:
        raise ValueError("Payroll period must have both start_date and end_date")

    if period.is_closed and not force_recalculate:
        raise ValueError("Payroll period is closed")

    with transaction.atomic():
        payroll, _ = EmployeePayroll.objects.select_for_update().get_or_create(
            employee=employee,
            period=period,
        )
        print(f"{payroll = }")

        if payroll.is_finalized and not force_recalculate:
            raise ValueError("Employee payroll is finalized")

        detail = _get_active_detail(employee)
        if not detail:
            raise ValueError("Active employee compensation is required")

        print(f"{detail = }")

        totals = _get_attendance_totals(employee, period)
        payload = _build_payroll_items(detail, totals)

        print(f"{totals = }")
        print(f"{payload = }")

        try:
            payroll.items.all().delete()
        except Exception as e:
            print(f"Error during delete payroll items: {e}")


        items_to_create = [
            PayrollItem(
                payroll=payroll,
                type=PayrollItem.ItemType.BASE,
                amount=payload["base_amount"],
                description="Base compensation",
            )
        ]

        if payload["overtime_amount"] > 0:
            items_to_create.append(
                PayrollItem(
                    payroll=payroll,
                    type=PayrollItem.ItemType.OVERTIME,
                    amount=payload["overtime_amount"],
                    description="Overtime compensation",
                )
            )

        if payload["penalty_amount"] > 0:
            items_to_create.append(
                PayrollItem(
                    payroll=payroll,
                    type=PayrollItem.ItemType.PENALTY,
                    amount=-payload["penalty_amount"],
                    description="Late and early leave penalty",
                )
            )
        print(f"{items_to_create = }")
        try:
            PayrollItem.objects.bulk_create(items_to_create)
        except Exception as e:
            print(f"Error during bulk create payroll items: {e}")

        total_amount = sum((item.amount for item in items_to_create), Decimal("0"))
        print(f"{total_amount = }")

        payroll.total_work_seconds = payload["work_seconds"]
        payroll.total_amount = total_amount.quantize(Decimal("0.01"))
        payroll.save(update_fields=["total_work_seconds", "total_amount", "calculated_at"])

        print(f"{payroll = }")
        print(f"Finished calculate employee payroll: {employee}")
        return payroll


def finalize_employee_payroll(payroll):
    if payroll.is_finalized:
        return payroll

    payroll.is_finalized = True
    payroll.save(update_fields=["is_finalized", "calculated_at"])
    return payroll
