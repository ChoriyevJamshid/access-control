import datetime

from apps.access_control.models import DailyAttendance
from apps.employees.models import Employee
from apps.payroll.models import PayrollPeriod


def get_attendance_data_for_period(enterprise_id: int, period: PayrollPeriod):
    """
    Returns:
        employees   — queryset of Employee ordered by last_name, first_name, middle_name
        dates       — sorted list of date objects within [period.start_date, period.end_date]
        attendance_map — dict {employee_id: {date: work_seconds}}
    """
    employees = (
        Employee.objects
        .filter(enterprise_id=enterprise_id)
        .order_by("last_name", "first_name", "middle_name")
    )

    # Build list of all dates in the period
    dates: list[datetime.date] = []
    current = period.start_date
    while current <= period.end_date:
        dates.append(current)
        current += datetime.timedelta(days=1)

    # Fetch attendance records as flat values (efficient)
    attendance_qs = (
        DailyAttendance.objects
        .filter(
            employee__enterprise_id=enterprise_id,
            date__gte=period.start_date,
            date__lte=period.end_date,
        )
        .values("employee_id", "date", "work_seconds")
    )

    attendance_map: dict[int, dict[datetime.date, int]] = {}
    for record in attendance_qs:
        emp_id = record["employee_id"]
        if emp_id not in attendance_map:
            attendance_map[emp_id] = {}
        attendance_map[emp_id][record["date"]] = record["work_seconds"]

    return employees, dates, attendance_map
