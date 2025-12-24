from django.db import models


# Create your models here.
class TenNhanVien(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ItemsCode(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    productType = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StopTime(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class ProductionProblem(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name