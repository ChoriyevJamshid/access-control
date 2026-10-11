from django.db.models import Q

from rest_framework import generics, filters
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend


from api.v1.access_control import serializers
from apps.access_control.models import AccessEvent, WorkSession, DailyAttendance


@extend_schema(tags=['AccessEvent'])
class AccessEventCreateAPIView(generics.CreateAPIView):
    queryset = AccessEvent.objects.all()
    serializer_class = serializers.AccessEventSerializer


@extend_schema(tags=['WorkSession'])
class WorkSessionListAPIView(generics.ListAPIView):
    queryset = WorkSession.objects.all()
    serializer_class = serializers.WorkSessionSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(employee__enterprise__owner=self.request.user)
            | Q(employee__enterprise__owner=self.request.user)
        )


@extend_schema(tags=['DailyAttendance'])
class DailyAttendanceListAPIView(generics.ListAPIView):
    serializer_class = serializers.DailyAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ['employee', 'date']
    search_fields = [
        'employee__first_name',
        'employee__last_name',
        'employee__middle_name',
    ]

    def get_queryset(self):
        return DailyAttendance.objects.filter(
            employee__enterprise__owner=self.request.user
        )




