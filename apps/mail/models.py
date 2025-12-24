from django.db import models


# Create your models here.
class Mail(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]
    mail_address = models.EmailField(unique=True)
    mail_person = models.CharField(max_length=100,blank=False)
    mail_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.mail_address
