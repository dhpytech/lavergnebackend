from django.db import models


class SafetyTime(models.Model):
    SAFETY_EVENT_TYPES = [('incident', 'INCIDENT'), ('accident', 'ACCIDENT'),]

    safety_date = models.DateField(verbose_name="Select Date")
    safety_type = models.CharField(max_length=50, choices=SAFETY_EVENT_TYPES)
    safety_description = models.TextField(verbose_name="Description of Occurrence")

    def __str__(self):
        return f"{self.safety_date} - {self.get_safety_type_display()} - {self.safety_description}"
