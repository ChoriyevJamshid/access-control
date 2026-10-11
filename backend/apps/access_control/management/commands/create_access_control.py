import random
import calendar
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.access_control.choices import AccessEventType
from apps.employees.models import Employee
from apps.access_control.models import AccessEvent


class Command(BaseCommand):
    help = 'Create test access control'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='Enterprise id'
        )

    def handle(self, *args, **options):

        employees = Employee.objects.filter(enterprise_id=options['id'])

        year = 2026
        month = 3
        total_days = calendar.monthrange(year, month)[1]

        for employee in employees:

            for day_number in range(1, total_days + 1):

                wd = calendar.weekday(year, month, day_number)
                if wd in (calendar.SATURDAY, calendar.SUNDAY):
                    continue

                hours = [8, 11, 14, 17]
                for hour in hours:
                    minutes = random.randint(1, 59)

                    dt = datetime(year=year, month=month, day=day_number,
                                  hour=hour, minute=minutes, second=0)
                    dt = timezone.make_aware(dt)

                    tp = AccessEventType.LEAVE
                    if hour in (8, 14):
                        tp = AccessEventType.ENTER

                    AccessEvent.objects.create(
                        employee=employee,
                        timestamp=dt,
                        type=tp
                    )
                    time.sleep(0.2)
                time.sleep(0.2)
            time.sleep(0.2)
