from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from unfold.admin import ModelAdmin, TabularInline

from .models import Department, DepartmentPart, Enterprise

User = get_user_model()


if User in admin.site._registry:
    admin.site.unregister(User)

if Group in admin.site._registry:
    admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(DjangoUserAdmin, ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "date_joined",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )

    ordering = ("-date_joined",)
    list_per_page = 50

    actions = ("activate_users", "deactivate_users")

    _SELF_DEACTIVATE_MSG = "You cannot deactivate your own account."
    _LAST_SUPERUSER_MSG = "You cannot deactivate or remove the last active superuser."

    def _is_last_active_superuser_change(self, user_id, new_is_active, new_is_superuser):
        current = User.objects.filter(pk=user_id).values("is_active", "is_superuser").first()

        if not current:
            return False

        was_active_superuser = current["is_active"] and current["is_superuser"]
        stays_active_superuser = bool(new_is_active) and bool(new_is_superuser)

        if not was_active_superuser or stays_active_superuser:
            return False

        has_other_active_superusers = User.objects.filter(
            is_superuser=True,
            is_active=True,
        ).exclude(pk=user_id).exists()

        return not has_other_active_superusers

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        updated = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f"Activated {updated} users.", level=messages.SUCCESS)

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        candidates = queryset.filter(is_active=True)
        protected_ids = set()

        if request.user.pk:
            protected_ids.add(request.user.pk)

        active_superuser_ids = set(
            User.objects.filter(is_superuser=True, is_active=True).values_list("pk", flat=True)
        )
        selected_active_superuser_ids = set(
            candidates.filter(is_superuser=True).values_list("pk", flat=True)
        )

        if active_superuser_ids and active_superuser_ids.issubset(selected_active_superuser_ids):
            if request.user.pk in active_superuser_ids:
                protected_ids.add(request.user.pk)
            else:
                protected_ids.add(min(active_superuser_ids))

        blocked = candidates.filter(pk__in=protected_ids).count()
        updated = candidates.exclude(pk__in=protected_ids).update(is_active=False)

        if updated:
            self.message_user(request, f"Deactivated {updated} users.", level=messages.WARNING)
        if blocked:
            self.message_user(
                request,
                f"Skipped {blocked} protected user(s): self account and/or last active superuser.",
                level=messages.ERROR,
            )

    def save_model(self, request, obj, form, change):
        if change:
            new_is_active = form.cleaned_data.get("is_active", obj.is_active)
            new_is_superuser = form.cleaned_data.get("is_superuser", obj.is_superuser)

            if obj.pk == request.user.pk and not new_is_active:
                form.add_error("is_active", self._SELF_DEACTIVATE_MSG)
                self.message_user(request, self._SELF_DEACTIVATE_MSG, level=messages.ERROR)
                return

            if self._is_last_active_superuser_change(obj.pk, new_is_active, new_is_superuser):
                form.add_error("is_superuser", self._LAST_SUPERUSER_MSG)
                self.message_user(request, self._LAST_SUPERUSER_MSG, level=messages.ERROR)
                return

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if obj.pk == request.user.pk:
            self.message_user(
                request,
                "You cannot delete your own account.",
                level=messages.ERROR,
            )
            return

        if obj.is_superuser and obj.is_active and not User.objects.filter(
            is_superuser=True,
            is_active=True,
        ).exclude(pk=obj.pk).exists():
            self.message_user(request, self._LAST_SUPERUSER_MSG, level=messages.ERROR)
            return

        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        protected_ids = set()

        if request.user.pk:
            protected_ids.add(request.user.pk)

        active_superuser_ids = set(
            User.objects.filter(is_superuser=True, is_active=True).values_list("pk", flat=True)
        )
        selected_active_superuser_ids = set(
            queryset.filter(is_superuser=True, is_active=True).values_list("pk", flat=True)
        )

        if active_superuser_ids and active_superuser_ids.issubset(selected_active_superuser_ids):
            if request.user.pk in active_superuser_ids:
                protected_ids.add(request.user.pk)
            else:
                protected_ids.add(min(active_superuser_ids))

        blocked = queryset.filter(pk__in=protected_ids).count()
        allowed_queryset = queryset.exclude(pk__in=protected_ids)
        deleted_count = allowed_queryset.count()

        super().delete_queryset(request, allowed_queryset)

        if blocked:
            self.message_user(
                request,
                f"Skipped {blocked} protected user(s): self account and/or last active superuser.",
                level=messages.ERROR,
            )
        if deleted_count:
            self.message_user(request, f"Deleted {deleted_count} users.", level=messages.WARNING)


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin, ModelAdmin):
    list_display = (
        "id",
        "name",
        "permissions_total",
        "users_total",
    )

    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 50

    @admin.display(description="Permissions", ordering="permissions_count")
    def permissions_total(self, obj):
        return obj.permissions_count

    @admin.display(description="Users", ordering="users_count")
    def users_total(self, obj):
        return obj.users_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            permissions_count=Count("permissions", distinct=True),
            users_count=Count("user", distinct=True),
        )


class DepartmentInline(TabularInline):
    model = Department
    extra = 0
    fields = ("name", "code", "parent")
    autocomplete_fields = ("parent",)
    readonly_fields = ("code",)
    ordering = ("name",)



@admin.register(Enterprise)
class EnterpriseAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "owner",
        "departments_total",
        "employees_total",
    )

    search_fields = (
        "name",
        "code",
        "owner__username",
    )

    list_filter = ("owner",)

    ordering = ("name",)

    autocomplete_fields = ("owner",)

    inlines = (DepartmentInline,)

    list_select_related = ("owner",)

    list_per_page = 50

    readonly_fields = ("created", "updated")

    actions = ("sync_codes",)

    @admin.display(description="Departments", ordering="departments_count")
    def departments_total(self, obj):
        return obj.departments_count

    @admin.display(description="Employees", ordering="employees_count")
    def employees_total(self, obj):
        return obj.employees_count

    @admin.action(description="Ensure enterprise codes")
    def sync_codes(self, request, queryset):
        updated = 0
        for enterprise in queryset.filter(code=""):
            enterprise.code = ""
            enterprise.save(update_fields=["code", "updated"])
            updated += 1
        self.message_user(
            request,
            f"Generated codes for {updated} enterprises.",
            level=messages.SUCCESS,
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("owner").annotate(
            departments_count=Count("departments", distinct=True),
            employees_count=Count("employees", distinct=True),
        )


@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "enterprise",
        "parent",
        "children_total",
    )

    search_fields = (
        "name",
        "code",
        "enterprise__name",
    )

    list_filter = (
        "enterprise",
    )

    ordering = ("enterprise__name", "name")

    autocomplete_fields = (
        "enterprise",
    )

    list_select_related = (
        "enterprise",
    )

    list_per_page = 50

    readonly_fields = ("created", "updated",)

    actions = ("promote_to_root",)

    @admin.display(description="Children", ordering="children_count")
    def children_total(self, obj):
        return obj.children_count

    @admin.action(description="Promote to top-level department")
    def promote_to_root(self, request, queryset):
        updated = queryset.exclude(parent__isnull=True).update(parent=None)
        self.message_user(
            request,
            f"Promoted {updated} departments to top-level.",
            level=messages.SUCCESS,
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True).select_related("enterprise").annotate(
            children_count=Count("children", distinct=True),
        )


@admin.register(DepartmentPart)
class DepartmentPartAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "parent",
        "enterprise",
        "employees_total",
    )

    search_fields = (
        "name",
        "code",
        "enterprise__name",
        "parent__name",
    )

    list_filter = (
        "enterprise",
        "parent",
    )

    ordering = ("enterprise__name", "name")

    autocomplete_fields = (
        "enterprise",
    )

    list_select_related = (
        "enterprise",
    )

    list_per_page = 50

    readonly_fields = ("created", "updated",)

    @admin.display(description="Employees", ordering="employees_count")
    def employees_total(self, obj):
        return obj.employees_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=False).select_related("enterprise", "parent").annotate(
            employees_count=Count("employees", distinct=True),
        )


