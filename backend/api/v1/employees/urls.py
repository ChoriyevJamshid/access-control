from django.urls import path

from api.v1.employees import views


urlpatterns = [
    path("create/", views.EmployeeCreateAPIView.as_view()),
    path("search/", views.EmployeeSearchAPIView.as_view()),
    path("employees/", views.EmployeeListAPIView.as_view()),
    path("employees/<int:pk>/", views.EmployeeDetailAPIView.as_view()),
    path("employees/<int:pk>/update/", views.EmployeeDetailUpdateAPIView.as_view()),
]



