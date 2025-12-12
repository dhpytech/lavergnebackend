from django.db import models


# Create your models here.
class Problem(models.Model):
    problem_code = models.CharField(max_length=100)
    problem_name = models.CharField(max_length=100)

    def __str__(self):
        return self.problem_name
