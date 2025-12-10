from django.db import models


# Create your models here.
class ItemCode(models.Model):
    ITEM_TYPES = [('nvl', 'NVL'), ('tp', 'TP'), ('semi-tp', 'SEMI-TP'), ('shaker', 'SHAKER')]
    item_name = models.CharField(max_length=100)
    item_description = models.TextField(blank=True)
    item_type = models.CharField(max_length=100,choices=ITEM_TYPES)

    def __str__(self):
        return f"{self.item_name}"
