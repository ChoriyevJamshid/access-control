from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
	total_employees = serializers.IntegerField()
	total_departments = serializers.IntegerField()
	today_present = serializers.IntegerField()
	today_present_percent = serializers.FloatField()
	today_present_change_percent = serializers.FloatField()
	today_late = serializers.IntegerField()
	today_late_percent = serializers.FloatField()
	today_late_change_percent = serializers.FloatField()


class DashboardActivityDaySerializer(serializers.Serializer):
	date = serializers.DateField()
	present_count = serializers.IntegerField()
	total_work_seconds = serializers.IntegerField()
	total_late_seconds = serializers.IntegerField()


class DashboardSeriesSerializer(serializers.Serializer):
	activity_7_days = DashboardActivityDaySerializer(many=True)


class DashboardAlertSerializer(serializers.Serializer):
	level = serializers.CharField()
	code = serializers.CharField()
	message = serializers.CharField()


class DashboardMetaSerializer(serializers.Serializer):
	as_of = serializers.DateField()
	timezone = serializers.CharField()


class DashboardResponseSerializer(serializers.Serializer):
	summary = DashboardSummarySerializer()
	series = DashboardSeriesSerializer()
	alerts = DashboardAlertSerializer(many=True)
	meta = DashboardMetaSerializer()
