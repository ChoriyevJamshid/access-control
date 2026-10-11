from django.db import models
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees import services
from api.v1.employees import serializers
from apps.employees.models import Employee, EmployeeDetail


@extend_schema(tags=['Employees'])
class EmployeeSearchAPIView(generics.GenericAPIView):
    serializer_class = serializers.EmployeeSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        enterprise = request.user.enterprise

        employee = services.get_employee(
            enterprise=enterprise,
            **serializer.validated_data
        )

        if not employee:
            return Response(
                {"detail": "Employee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(employee)


@extend_schema(tags=["Employees"])
class EmployeeListAPIView(generics.ListAPIView):
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        enterprise = self.request.user.enterprise

        return (
            Employee.objects
            .filter(department__enterprise=enterprise)
            .select_related("department", "department__enterprise")
            .order_by("last_name", "first_name")
        )


# @extend_schema(tags=['Employees'])
# class EmployeeCreateAPIView(generics.CreateAPIView):
#     queryset = Employee.objects.all()
#     serializer_class = serializers.EmployeeSerializer


@extend_schema(tags=["Employee"])
class EmployeeCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.EmployeeCreateSerializer


@extend_schema(tags=['Employees'])
class EmployeeDetailAPIView(generics.RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


from .serializers import EmployeeDetailUpdateSerializer
from .services import update_employee_compensation


@extend_schema(tags=["Employees"])
class EmployeeDetailUpdateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.EmployeeDetailUpdateSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            return Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return None

    def patch(self, request, *args, **kwargs):
        employee = self.get_object()
        if not employee:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = super().get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_employee_compensation(
            employee,
            serializer.validated_data
        )

        return Response(
            {"detail": "Compensation updated"},
            status=status.HTTP_200_OK
        )


