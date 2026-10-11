from django.urls import path

from api.v1.payroll.views import (
    PayrollPeriodListAPIView,
    CreatePayrollAPIView,
    RecalculatePayrollPeriodAPIView,
    EmployeePayrollListAPIView,
    EmployeePayrollDetailAPIView,
    FinalizeEmployeePayrollAPIView,
    FinalizeEmployeePayrollListAPIView,
    PayrollAttendanceExcelAPIView,
)

urlpatterns = [
    path("", PayrollPeriodListAPIView.as_view()),
    path("create/", CreatePayrollAPIView.as_view()),
    path("<int:period_id>/recalculate/", RecalculatePayrollPeriodAPIView.as_view()),
    path("<int:period_id>/employees/", EmployeePayrollListAPIView.as_view()),
    path("<int:period_id>/attendance-excel/", PayrollAttendanceExcelAPIView.as_view()),
    path("employee-payrolls/<int:pk>/", EmployeePayrollDetailAPIView.as_view()),
    path("employee-payrolls/finalize/", FinalizeEmployeePayrollListAPIView.as_view()),
    path("employee-payrolls/<int:payroll_id>/finalize/", FinalizeEmployeePayrollAPIView.as_view()),
]

