from datetime import datetime

from django.core.management.base import BaseCommand

from apps.payroll.models import PayrollPeriod
from apps.users.models import Enterprise, Department

class Command(BaseCommand):
    help = 'Create test employees' #

    def add_arguments(self, parser):
        parser.add_argument(
            "--dep",
            type=int,
            default=1,
            help="Department number"
        )

        parser.add_argument(
            "--part",
            type=int,
            default=1,
            help="Part number for each department"
        )


    def handle(self, *args, **options):

        dep_count = options['dep']
        part_count = options['part']

        enterprise = Enterprise.objects.create(
            name='Enterprise #1',
            owner_id=1
        )

        for i in range(1, dep_count + 1):
            department = Department.objects.create(
                name=f'Department #{i}',
                enterprise=enterprise
            )

            for j in range(1, part_count + 1):
                Department.objects.create(
                    name=f'Part #{(i - 1) * part_count + j}',
                    enterprise=enterprise,
                    parent=department
                )

        PayrollPeriod.objects.create(
            start_date=datetime(2026, 1, 1).date(),
            end_date=datetime(2026, 1, 31).date(),
        )

        self.stdout.write(f'Created enterprise: {enterprise.code}!')



