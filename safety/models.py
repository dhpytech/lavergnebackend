from django.db import models


class SafetyTime(models.Model):
    SAFETY_EVENT_TYPES = [('incident', 'INCIDENT'), ('accident', 'ACCIDENT'), ('sop', 'SOP'),]

    safety_date = models.DateTimeField(verbose_name="Select Date & Time")
    safety_type = models.CharField(max_length=50, choices=SAFETY_EVENT_TYPES)
    safety_description = models.TextField(verbose_name="Description of Occurrence")

    def __str__(self):
        return f"{self.safety_date} - {self.get_safety_type_display()} - {self.safety_description}"
