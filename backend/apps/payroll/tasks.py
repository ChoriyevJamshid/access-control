from celery import shared_task
from django.db import connection

from apps.employees.models import Employee
from apps.payroll.models import PayrollPeriod
from apps.payroll.services import calculate_employee_payroll


@shared_task(bind=True, max_retries=3)
def recalculate_employee_payroll_task(self, employee_id: int, period_id: int, force_recalculate: bool = True):
    try:
        employee = Employee.objects.select_related("enterprise").filter(id=employee_id).first()
        period = PayrollPeriod.objects.filter(id=period_id).first()

        if not employee or not period:
            print(f"Recalculate skipped: employee={employee_id} or period={period_id} not found")
            return

        calculate_employee_payroll(
            employee,
            period,
            force_recalculate=force_recalculate,
        )
    except ValueError as exc:
        print(f"Recalculate skipped for employee={employee_id}, period={period_id}: {exc}")
        return
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@shared_task(bind=True, max_retries=3)
def recalculate_payroll_period_task(self, enterprise_id: int, period_id: int):
    try:
        period = PayrollPeriod.objects.filter(id=period_id).first()
        if not period:
            print(f"Period recalculate skipped: period={period_id} not found")
            return
        print(f"{period = }")
        employee_ids = list(
            Employee.objects
            .filter(enterprise_id=enterprise_id)
            .values_list("id", flat=True)
        )

        # SQLite allows only limited concurrent writes; process sequentially to avoid lock storms.
        if connection.vendor == "sqlite":
            for employee_id in employee_ids:
                employee = Employee.objects.select_related("enterprise").filter(id=employee_id).first()
                if not employee:
                    continue

                try:
                    calculate_employee_payroll(
                        employee,
                        period,
                        force_recalculate=True,
                    )
                except ValueError as exc:
                    print(f"Period recalculate skipped for employee={employee_id}, period={period_id}: {exc}")
                    continue

            return

        for employee_id in employee_ids:
            recalculate_employee_payroll_task.delay(
                employee_id=employee_id,
                period_id=period.id,
                force_recalculate=True,
            )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
