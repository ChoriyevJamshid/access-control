from django.urls import path, include

urlpatterns = [
    path("dashboard/", include("api.v1.dashboard.urls")),
    path("access-controls/", include("api.v1.access_control.urls")),
    path("employees/", include("api.v1.employees.urls")),
    path("enterprise/", include("api.v1.enterprise.urls")),
    path("payroll-periods/", include("api.v1.payroll.urls")),
]



