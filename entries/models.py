from django.db import models


class MarisInput(models.Model):
    date = models.DateField()
    shift = models.CharField(max_length=20)
    employee = models.CharField(max_length=100,null=True,blank=True)
    mainData = models.JSONField(blank=True)
    stopTimes = models.JSONField(blank=True, null=True)
    problems = models.JSONField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"MarisInput {self.id} - {self.date} - {self.employee}"

