from django.db.models import TextChoices


class AccessEventType(TextChoices):
    ENTER = 'enter', 'enter'
    LEAVE = 'leave', 'leave'


