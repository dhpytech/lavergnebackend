from django.db import models
from django.utils.translation import gettext_lazy as _


class ShiftType(models.TextChoices):
    DAY = 'Day', _('Day')
    NIGHT = 'Night', _('Night')
