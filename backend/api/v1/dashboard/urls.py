from django.urls import path

from api.v1.dashboard import views


urlpatterns = [
    path("", views.DashboardAPIView.as_view(), name="dashboard"),
]


