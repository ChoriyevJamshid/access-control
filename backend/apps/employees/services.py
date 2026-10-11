from django.db import models
from apps.employees.models import Employee
from apps.users.models import Enterprise


def get_employee(enterprise, first_name=None, last_name=None, middle_name=None, code=None):
    qs = (
        Employee.objects
        .filter(department__enterprise=enterprise)
        .select_related("department")
    )

    if code:
        return qs.filter(code=code).values(
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "code"
        ).first()

    if first_name and last_name and middle_name:
        return qs.filter(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name
        ).values(
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "code"
        ).first()

    return None
