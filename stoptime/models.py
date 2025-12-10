from django.db import models


# Create your models here.
class StopTime(models.Model):
    stop_time_name = models.CharField(max_length=100)
    stop_time_description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.stop_time_name}"
