from rest_framework import serializers

from apps.access_control import services
from apps.access_control.models import AccessEvent, WorkSession, DailyAttendance
from apps.employees.models import Employee


class AccessEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessEvent
        fields = ('employee', 'timestamp', 'type')

    def create(self, validated_data):
        is_exists = services.check_access_exists_service(
            employee=validated_data['employee'],
            timestamp=validated_data['timestamp'],
            event_type=validated_data['type'])

        if is_exists:
            raise serializers.ValidationError(detail='AccessEvent already exists.',
                                              code=403)

        return super().create(validated_data)


class WorkSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSession
        fields = '__all__'


class DailyAttendanceSerializer(serializers.ModelSerializer):

    employee = serializers.SerializerMethodField()

    class Meta:
        model = DailyAttendance
        fields = (
            'employee',
            'date',
            'work_seconds',
            'late_seconds',
            'planned_seconds',
            'early_leave_seconds'
        )

    def get_employee(self, obj):
        return obj.employee.get_full_name