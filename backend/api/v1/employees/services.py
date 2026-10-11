# services.py

from django.db import transaction
from apps.employees.models import EmployeeDetail, EmployeeWorkDay


def update_employee_compensation(employee, validated_data):
    work_days_data = validated_data.pop("work_days")

    with transaction.atomic():

        current_detail = employee.details.filter(is_active=True).first()

        if current_detail:
            current_detail.is_active = False
            current_detail.effective_to = validated_data["effective_from"]
            current_detail.save(update_fields=["is_active", "effective_to"])

        new_detail = EmployeeDetail.objects.create(
            employee=employee,
            is_active=True,
            **validated_data
        )

        work_days = [
            EmployeeWorkDay(
                detail=new_detail,
                **wd
            )
            for wd in work_days_data
        ]

        EmployeeWorkDay.objects.bulk_create(work_days)

        return new_detail