from django.contrib import admin, messages
from unfold.admin import ModelAdmin

from .models import AccessEvent, WorkSession, DailyAttendance


@admin.register(AccessEvent)
class AccessEventAdmin(ModelAdmin):
    list_display = (
        "id",
        "employee",
        "employee_code",
        "type",
        "timestamp",
    )

    list_filter = (
        "type",
        "timestamp",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__code",
    )

    date_hierarchy = "timestamp"

    ordering = ("-timestamp",)

    list_select_related = ("employee",)

    autocomplete_fields = ("employee",)

    list_per_page = 50

    readonly_fields = ("created", "updated")

    @admin.display(description="Employee code", ordering="employee__code")
    def employee_code(self, obj):
        return obj.employee.code

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("employee")


@admin.register(WorkSession)
class WorkSessionAdmin(ModelAdmin):
    list_display = (
        "id",
        "employee",
        "started",
        "ended",
        "duration_hours",
        "closed",
        "session_status",
    )

    list_filter = (
        "closed",
        "started",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__code",
    )

    ordering = ("-started",)

    list_select_related = ("employee",)

    autocomplete_fields = ("employee",)

    readonly_fields = (
        "duration_seconds",
        "created",
        "updated",
    )

    list_per_page = 50

    actions = ("mark_closed",)

    @admin.display(description="Hours")
    def duration_hours(self, obj):
        if not obj.duration_seconds:
            return "-"
        hours = obj.duration_seconds // 3600
        minutes = (obj.duration_seconds % 3600) // 60

        return f"{hours:02d}:{minutes:02d}"

    @admin.display(description="Status")
    def session_status(self, obj):
        return "Closed" if obj.closed else "Open"

    @admin.action(description="Mark selected sessions as closed")
    def mark_closed(self, request, queryset):
        updated = queryset.filter(closed=False).update(closed=True)
        self.message_user(request, f"{updated} sessions were closed.", level=messages.SUCCESS)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("employee")


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(ModelAdmin):
    list_display = (
        "id",
        "employee",
        "date",
        "work_hours",
        "late_hours",
        "overtime_hours",
    )

    list_filter = (
        "date",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__code",
    )

    ordering = ("-date",)

    list_select_related = ("employee",)

    autocomplete_fields = ("employee",)

    readonly_fields = (
        "created",
        "updated",
    )

    list_per_page = 50

    date_hierarchy = "date"

    @admin.display(description="Hours")
    def work_hours(self, obj):
        if not obj.work_seconds:
            return "-"
        hours = obj.work_seconds // 3600
        minutes = (obj.work_seconds % 3600) // 60

        return f"{hours:02d}:{minutes:02d}"

    @admin.display(description="Late")
    def late_hours(self, obj):
        if not obj.late_seconds:
            return "-"
        hours = obj.late_seconds // 3600
        minutes = (obj.late_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    @admin.display(description="Overtime")
    def overtime_hours(self, obj):
        if not obj.overtime_seconds:
            return "-"
        hours = obj.overtime_seconds // 3600
        minutes = (obj.overtime_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("employee")

