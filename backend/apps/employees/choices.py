from django.db.models import TextChoices


class SalaryType(TextChoices):
    HOURLY = "hourly", "Hourly"
    MONTHLY = "monthly", "Monthly"


class DayChoice(TextChoices):
    MONDAY = "monday", "Monday"
    TUESDAY = "tuesday", "Tuesday"
    WEDNESDAY = "wednesday", "Wednesday"
    THURSDAY = "thursday", "Thursday"
    FRIDAY = "friday", "Friday"
    SATURDAY = "saturday", "Saturday"
    SUNDAY = "sunday", "Sunday"


