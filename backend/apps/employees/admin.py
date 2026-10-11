from django.contrib import admin, messages
from django.db.models import Count, Exists, OuterRef
from unfold.admin import ModelAdmin, StackedInline, TabularInline

from .models import Employee, EmployeeDetail, EmployeeWorkDay


class EmployeeWorkDayInline(TabularInline):
    model = EmployeeWorkDay
    extra = 0
    min_num = 0
    fields = (
        "weekday",
        "from_time",
        "to_time",
        "hours",
    )
    ordering = ("weekday",)


class EmployeeDetailInline(StackedInline):
    model = EmployeeDetail
    extra = 0
    min_num = 0
    show_change_link = True
    fields = (
        "salary_type",
        "amount",
        "effective_from",
        "effective_to",
        "is_active",
    )
    readonly_fields = ()


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "enterprise",
        "department",
        "code",
        "has_active_salary",
    )

    list_filter = (
        "enterprise",
        "department",
    )

    search_fields = (
        "first_name",
        "last_name",
        "middle_name",
        "code",
    )

    ordering = ("last_name", "first_name")

    autocomplete_fields = (
        "enterprise",
        "department",
    )

    inlines = (
        EmployeeDetailInline,
    )

    list_select_related = (
        "enterprise",
        "department",
    )

    list_per_page = 50

    actions = ("assign_department_enterprise",)

    @admin.display(description="Full name", ordering="last_name")
    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name}"

    @admin.display(boolean=True, description="Active salary")
    def has_active_salary(self, obj):
        return obj.has_active_salary

    @admin.action(description="Sync enterprise from department")
    def assign_department_enterprise(self, request, queryset):
        updated = 0
        for employee in queryset.select_related("department", "enterprise"):
            if employee.department and employee.enterprise_id != employee.department.enterprise_id:
                employee.enterprise = employee.department.enterprise
                employee.save(update_fields=["enterprise", "updated"])
                updated += 1

        self.message_user(
            request,
            f"Enterprise synchronized for {updated} employees.",
            level=messages.SUCCESS,
        )

    def get_queryset(self, request):
        active_detail_qs = EmployeeDetail.objects.filter(
            employee_id=OuterRef("pk"),
            is_active=True,
        )
        qs = super().get_queryset(request)
        return qs.select_related("enterprise", "department").annotate(
            has_active_salary=Exists(active_detail_qs),
        )


@admin.register(EmployeeDetail)
class EmployeeDetailAdmin(ModelAdmin):
    list_display = (
        "id",
        "employee",
        "salary_type",
        "amount",
        "effective_from",
        "effective_to",
        "is_active",
        "work_days_count",
    )

    list_filter = (
        "salary_type",
        "is_active",
        "effective_from",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__code",
    )

    autocomplete_fields = (
        "employee",
    )

    inlines = (
        EmployeeWorkDayInline,
    )

    list_select_related = (
        "employee",
    )

    ordering = ("-effective_from",)

    list_per_page = 50

    actions = ("mark_as_active", "mark_as_inactive")

    @admin.display(description="Work days", ordering="work_days_total")
    def work_days_count(self, obj):
        return obj.work_days_total

    @admin.action(description="Mark selected as active")
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} detail rows marked active.", level=messages.SUCCESS)

    @admin.action(description="Mark selected as inactive")
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} detail rows marked inactive.", level=messages.WARNING)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("employee").annotate(work_days_total=Count("work_days", distinct=True))


@admin.register(EmployeeWorkDay)
class EmployeeWorkDayAdmin(ModelAdmin):
    list_display = (
        "id",
        "detail",
        "weekday",
        "from_time",
        "to_time",
        "hours",
    )

    list_filter = (
        "weekday",
    )

    search_fields = (
        "detail__employee__first_name",
        "detail__employee__last_name",
    )

    autocomplete_fields = (
        "detail",
    )

    list_select_related = (
        "detail",
        "detail__employee",
    )

    ordering = ("weekday",)

    list_per_page = 100

