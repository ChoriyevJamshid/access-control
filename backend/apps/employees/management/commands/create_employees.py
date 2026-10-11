import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.employees.choices import SalaryType
from apps.employees.models import Employee, EmployeeDetail, EmployeeWorkDay
from apps.users.models import Enterprise, Department


class Command(BaseCommand):
    help = 'Create test employees' #

    def add_arguments(self, parser):

        parser.add_argument(
            "--id",
            type=int,
            required=True,
            help="Enterprise id",
        )

        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of employees for each department",
        )

    def handle(self, *args, **options):

        enterprise_id = options["id"]
        count = options["count"]

        try:
            enterprise = Enterprise.objects.get(id=enterprise_id)
        except Enterprise.DoesNotExist:
            raise CommandError(f"Enterprise with id {enterprise_id} does not exist")

        departments = Department.objects.filter(enterprise=enterprise,
                                                parent__isnull=False)

        for i, department in enumerate(departments):

            for j in range(1, count + 1):
                x = i * count
                employee = Employee.objects.create(
                    enterprise=enterprise,
                    department=department,
                    first_name=f'FirstName_{x + j}',
                    last_name=f'LastName_{x + j}',
                    middle_name=f'MiddleName_{x + j}',
                    code=f'Code_{x + j}'
                )

                detail = EmployeeDetail.objects.create(
                    employee=employee,
                    salary_type=SalaryType.HOURLY,
                    amount=random.choice([price for price in range(5000, 15001, 1000)]),
                    effective_from=timezone.now().date()
                )

                work_days = []
                for k in range(5):
                    work_days.append(EmployeeWorkDay(
                        detail=detail,
                        weekday=k,
                        from_time="08:30",
                        to_time="18:30",
                        hours=timedelta(hours=8)
                    ))

                EmployeeWorkDay.objects.bulk_create(work_days)
                self.stdout.write(f'Created employee {employee}!')



