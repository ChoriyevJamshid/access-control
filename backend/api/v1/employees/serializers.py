from django.db import transaction
from rest_framework import serializers

from apps.users.models import Department
from apps.employees.models import (Employee,
                                   EmployeeDetail,
                                   EmployeeWorkDay)


class _DepartmentSerializer(serializers.ModelSerializer):
    parent = serializers.StringRelatedField(source='parent.name', read_only=True)

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'code',
            'parent',
        )


class _WorkDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeWorkDay
        fields = (
            'id',
            'weekday',
            'from_time',
            'to_time',
            'hours'
        )


class _EmployeeDetailSerializer(serializers.ModelSerializer):
    work_days = _WorkDaySerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeDetail
        fields = (
            'salary_type',
            'amount',
            'effective_from',
            'effective_to',
            'work_days',
        )


class EmployeeSerializer(serializers.ModelSerializer):
    department = _DepartmentSerializer(many=False, read_only=True)
    detail = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'code',
            'department',
            'detail'
        )

    def get_detail(self, obj):
        active_detail = obj.details.filter(is_active=True).first()
        if active_detail:
            return _EmployeeDetailSerializer(active_detail).data
        return None


class EmployeeSearchSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    middle_name = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    def validate(self, attrs):
        if not any([
            attrs.get("code"),
            (
                    attrs.get("first_name") and
                    attrs.get("last_name") and
                    attrs.get("middle_name")
            )
        ]):
            raise serializers.ValidationError(
                "Provide code or full name."
            )
        return attrs


class EmployeeWorkDayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeWorkDay
        fields = (
            "weekday",
            "from_time",
            "to_time",
            "hours",
        )


class EmployeeDetailCreateSerializer(serializers.ModelSerializer):
    work_days = EmployeeWorkDayCreateSerializer(many=True)

    class Meta:
        model = EmployeeDetail
        fields = (
            "salary_type",
            "amount",
            "effective_from",
            "effective_to",
            "is_active",
            "work_days",
        )


class EmployeeCreateSerializer(serializers.ModelSerializer):
    detail = EmployeeDetailCreateSerializer(write_only=True)

    class Meta:
        model = Employee
        fields = (
            "department",
            "first_name",
            "last_name",
            "middle_name",
            "code",
            "detail",
        )

    def validate_code(self, value):
        if Employee.objects.filter(code=value).exists():
            raise serializers.ValidationError("Employee already exists.")
        return value

    def create(self, validated_data):
        detail_data = validated_data.pop("detail")
        work_days_data = detail_data.pop("work_days")

        with transaction.atomic():
            employee = Employee.objects.create(**validated_data)

            detail = EmployeeDetail.objects.create(
                employee=employee,
                **detail_data
            )

            work_days = [
                EmployeeWorkDay(
                    detail=detail,
                    **wd
                )
                for wd in work_days_data
            ]

            EmployeeWorkDay.objects.bulk_create(work_days)

        return employee


class EmployeeDetailUpdateSerializer(serializers.Serializer):
    salary_type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)

    work_days = _WorkDaySerializer(many=True)

    def validate_work_days(self, value):
        weekdays = [wd["weekday"] for wd in value]
        if len(weekdays) != len(set(weekdays)):
            raise serializers.ValidationError(
                "Duplicate weekdays are not allowed."
            )
        return value
