from django.db import models
from shared.models import TrackingModel
from shared.constants import ShiftType


class BaseProductionEntry(TrackingModel):
    date = models.DateField(db_index=True)
    shift = models.CharField(
        max_length=50,
        choices=ShiftType.choices,
        default=ShiftType.DAY,
        db_index=True
    )
    employee = models.CharField(max_length=100, db_index=True, null=True)
    production_data = models.JSONField(default=list, blank=True)

    class Meta:
        abstract = True
        ordering = ['-date', '-created_at']


# 1. MARIS:
class MarisInput(BaseProductionEntry):
    stop_time_data = models.JSONField(default=list, blank=True, null=True)
    problem_data = models.JSONField(default=list, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta(BaseProductionEntry.Meta):
        verbose_name = "Maris Production Entry"


# 2. METAL: Có thêm số Lô (LOT)
class MetalInput(BaseProductionEntry):
    lot_number = models.CharField(max_length=50, db_index=True)

    class Meta(BaseProductionEntry.Meta):
        verbose_name = "Metal Production Entry"


# 3. BAGGING: Có thêm nhân viên thứ 2 và số Lô (LOT)
class BaggingInput(BaseProductionEntry):
    employee_2 = models.CharField(max_length=100, db_index=True, null=True)
    lot_number = models.CharField(max_length=50, db_index=True)

    class Meta(BaseProductionEntry.Meta):
        verbose_name = "Bagging Production Entry"
