from django.db import models


# Create your models here.
class DlncCase(models.Model):
    dlnc_case_name = models.CharField(max_length=100)
    dlnc_case_description = models.CharField(max_length=100)

    def __str__(self):
        return self.dlnc_case_name
