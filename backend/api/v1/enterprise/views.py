from django.db import models
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.v1.enterprise import serializers
from apps.users.models import Enterprise, Department


@extend_schema(tags=["Enterprise"])
class EnterpriseAPIView(generics.RetrieveAPIView):
    queryset = Enterprise.objects.all()
    serializer_class = serializers.EnterpriseSerializer

    def get_object(self):
        return get_object_or_404(
            Enterprise.objects.select_related("owner"),
            owner=self.request.user
        )


@extend_schema(tags=["Enterprise"])
class DepartmentListAPIView(generics.ListAPIView):
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        enterprise = self.request.user.enterprise

        return (
            Department.objects
            .filter(
                enterprise=enterprise,
                parent__isnull=True  # только root
            )
            .annotate(total_employees=models.Count("children__employees",
                                                   distinct=True))
            .select_related("enterprise")
            .prefetch_related("children")
            .order_by("name")
        )


@extend_schema(tags=["Enterprise"])
class DepartmentDetailAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        enterprise = self.request.user.enterprise

        return (
            Department.objects
            .filter(
                enterprise=enterprise,
                parent__isnull=True  # только root
            )
            .select_related("enterprise")
            .prefetch_related("children")
            .order_by("name")
        )


@extend_schema(tags=["Department"])
class DepartmentCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.DepartmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Department.objects.filter(
            enterprise=self.request.user.enterprise
        )


