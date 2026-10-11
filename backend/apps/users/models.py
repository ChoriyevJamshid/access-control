import random

from django.db import models
from django.contrib.auth import get_user_model

from apps.base_models import BaseModel

User = get_user_model()


class Enterprise(BaseModel):
    name = models.CharField(max_length=63, db_index=True)
    code = models.CharField(max_length=63, unique=True, blank=True)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="enterprise"
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def save(self, *args, **kwargs):

        if not self.code:

            while True:
                code = random.randint(1_000_000_000, 9_999_999_999)
                code = "ENT-" + str(code)
                if not self.__class__.objects.filter(code=code).exists():
                    break

            self.code = code

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(BaseModel):
    name = models.CharField(max_length=63, db_index=True)
    code = models.CharField(max_length=63, unique=True, blank=True)

    enterprise = models.ForeignKey(
        "Enterprise",
        on_delete=models.CASCADE,
        related_name='departments',
        db_index=True,
        blank=True,
        null=True
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children"
    )

    class Meta:
        ordering = ['enterprise__name', 'name']
        indexes = [
            models.Index(fields=['enterprise', 'name']),
            models.Index(fields=["parent"])
        ]
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['enterprise', 'name'],
        #         name='unique_department_name_per_enterprise'
        #     )
        # ]

    # def clean(self):
    #     if self.parent and self.parent.enterprise != self.enterprise:
    #         raise ValidationError("Parent must belong to same enterprise")


    def save(self, *args, **kwargs):

        if not self.code:

            while True:
                code = random.randint(1_000_000_000, 9_999_999_999)
                code = "DEP-" + str(code)
                if not self.__class__.objects.filter(code=code).exists():
                    break

            self.code = code

        if self.parent and self.enterprise != self.parent.enterprise:
            self.enterprise = self.parent.enterprise

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


class DepartmentPart(Department):
    class Meta:
        proxy = True



