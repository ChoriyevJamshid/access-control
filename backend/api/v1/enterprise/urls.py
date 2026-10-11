from django.urls import path

from api.v1.enterprise import views


urlpatterns = [
    path("enterprise/", views.EnterpriseAPIView.as_view()),
    path("departments/", views.DepartmentListAPIView.as_view()),
    path("departments/create/", views.DepartmentCreateAPIView.as_view()),
    path("departments/<int:pk>/", views.DepartmentDetailAPIView.as_view()),
]


