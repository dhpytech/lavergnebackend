from django.db import models


# Create your models here.
class Employee(models.Model):
    employee_id = models.CharField(primary_key=True)
    employee_name = models.CharField(max_length=100)
    employee_position = models.CharField(max_length=100)

    def __str__(self):
        return self.employee_name
