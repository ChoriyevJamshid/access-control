from django.contrib import admin, messages
from django.db.models import Count
from unfold.admin import ModelAdmin, TabularInline

from apps.payroll.models import EmployeePayroll, PayrollItem, PayrollPeriod


# =========================
# PayrollItem Inline
# =========================

class PayrollItemInline(TabularInline):
    model = PayrollItem
    extra = 0
    autocomplete_fields = ()
    readonly_fields = ()
    fields = ("type", "amount", "description")
    ordering = ("type",)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_finalized:
            return False
        return super().has_delete_permission(request, obj)


# =========================
# PayrollPeriod Admin
# =========================

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(ModelAdmin):
    list_display = (
        "id",
        "start_date",
        "end_date",
        "is_closed",
        "employee_count",
    )

    list_filter = ("is_closed", "start_date")
    search_fields = ("start_date", "end_date")
    ordering = ("-start_date",)

    actions = ["close_period", "reopen_period"]

    @admin.display(description="Employees", ordering="employee_payrolls_count")
    def employee_count(self, obj):
        return obj.employee_payrolls_count

    @admin.action(description="Close selected periods")
    def close_period(self, request, queryset):
        updated = queryset.filter(is_closed=False).update(is_closed=True)
        self.message_user(request, f"Closed {updated} payroll periods.", level=messages.SUCCESS)

    @admin.action(description="Reopen selected periods")
    def reopen_period(self, request, queryset):
        updated = queryset.filter(is_closed=True).update(is_closed=False)
        self.message_user(request, f"Reopened {updated} payroll periods.", level=messages.WARNING)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(employee_payrolls_count=Count("employee_payrolls", distinct=True))

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_closed:
            return False
        return super().has_delete_permission(request, obj)


# =========================
# EmployeePayroll Admin
# =========================

@admin.register(EmployeePayroll)
class EmployeePayrollAdmin(ModelAdmin):
    list_display = (
        "id",
        "employee",
        "period",
        "total_work_seconds",
        "total_amount",
        "get_compensation_amount",
        "is_finalized",
        "calculated_at",
    )

    list_filter = (
        "is_finalized",
        "period",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
    )

    autocomplete_fields = ("employee", "period")
    readonly_fields = ("calculated_at",)

    inlines = [PayrollItemInline]

    actions = ["finalize_payroll"]

    list_per_page = 50

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("employee", "period")

    @admin.action(description="Finalize selected payrolls")
    def finalize_payroll(self, request, queryset):
        updated = queryset.filter(is_finalized=False).update(is_finalized=True)
        self.message_user(request, f"Finalized {updated} payroll rows.", level=messages.SUCCESS)

    @admin.display(description="Amount")
    def get_compensation_amount(self, obj):
        comp = obj.employee.details.filter(is_active=True).first()
        if not comp:
            return '----'
        return comp.amount

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_finalized:
            return False
        return super().has_delete_permission(request, obj)


# =========================
# PayrollItem Admin
# =========================

@admin.register(PayrollItem)
class PayrollItemAdmin(ModelAdmin):
    list_display = (
        "id",
        "payroll",
        "type",
        "amount",
        "description",
    )

    list_filter = ("type",)
    search_fields = (
        "payroll__employee__first_name",
        "payroll__employee__last_name",
        "description",
    )

    autocomplete_fields = ("payroll",)

    list_per_page = 100

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("payroll", "payroll__employee")

    def has_delete_permission(self, request, obj=None):
        if obj and obj.payroll.is_finalized:
            return False
        return super().has_delete_permission(request, obj)