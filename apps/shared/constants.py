from django.db import models
from django.utils.translation import gettext_lazy as _


class ShiftType(models.TextChoices):
    DAY = 'DAY', _('Day Shift')
    NIGHT = 'NIGHT', _('Night Shift')
