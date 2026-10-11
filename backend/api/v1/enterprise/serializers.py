from rest_framework import serializers

from apps.users.models import Enterprise, Department


class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'


class DepartmentChildSerializer(serializers.ModelSerializer):
    total_employees = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ("id", "name", "code", "total_employees")

    def get_total_employees(self, obj):
        return obj.employees.count()


class DepartmentSerializer(serializers.ModelSerializer):
    children = DepartmentChildSerializer(many=True, read_only=True)
    total_employees = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ("id", "name", "code", "total_employees", "children")


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            "name",
            "parent",
        )

    def validate_parent(self, parent):
        request = self.context["request"]
        user = request.user

        if parent and parent.enterprise != user.enterprise:
            raise serializers.ValidationError(
                "Parent department must belong to your enterprise."
            )
        return parent

    def create(self, validated_data):
        request = self.context["request"]

        department = Department.objects.create(
            enterprise=request.user.enterprise,
            **validated_data
        )
        return department
