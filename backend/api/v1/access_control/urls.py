from django.urls import path

from api.v1.access_control import views



urlpatterns = [
    path('create/', views.AccessEventCreateAPIView.as_view()),


    path("work-sessions/", views.WorkSessionListAPIView.as_view()),

    path("daily-attendances/", views.DailyAttendanceListAPIView.as_view()),
]

