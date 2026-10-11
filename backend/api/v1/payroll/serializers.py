from rest_framework import serializers
from django.db import IntegrityError, transaction

from apps.payroll.models import (PayrollPeriod,
                                 EmployeePayroll,
                                 PayrollItem)


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if not start_date:
            raise serializers.ValidationError({"start_date": "Start date is required"})

        if start_date >= end_date:
            raise serializers.ValidationError("Start date must be before end date")

        last_pp = PayrollPeriod.objects.order_by('-end_date', '-created').first()
        if last_pp and start_date <= last_pp.end_date:
            raise serializers.ValidationError(
                {"start_date": "Start date must be after last period end date"}
            )

        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                last_pp = PayrollPeriod.objects.select_for_update().order_by('-end_date', '-created').first()
                if last_pp and validated_data['start_date'] <= last_pp.end_date:
                    raise serializers.ValidationError(
                        {"start_date": "Start date must be after last period end date"}
                    )

                return PayrollPeriod.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError("Payroll period overlaps with an existing record")


class PayrollItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollItem
        fields = ["id", "type", "amount", "description", "created"]


class EmployeePayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    period_start = serializers.DateField(source="period.start_date", read_only=True)
    period_end = serializers.DateField(source="period.end_date", read_only=True)
    items = PayrollItemSerializer(many=True, read_only=True)

    class Meta:
        model = EmployeePayroll
        fields = [
            "id",
            "employee",
            "employee_name",
            "period",
            "period_start",
            "period_end",
            "total_work_seconds",
            "total_amount",
            "is_finalized",
            "calculated_at",
            "items",
        ]


class RecalculatePayrollPeriodSerializer(serializers.Serializer):
    period_id = serializers.IntegerField()


class FinalizePayrollSerializer(serializers.Serializer):
    payroll_id = serializers.IntegerField()

class FinalizePayrollListSerializer(serializers.Serializer):
    payroll_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )