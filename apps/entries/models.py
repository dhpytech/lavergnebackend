from django.db import models
from shared.models import TrackingModel
from shared.constants import ShiftType


class MarisInput(TrackingModel):  # Kế thừa TrackingModel để có created_at, updated_at
    # 1. Header Information
    date = models.DateField(db_index=True)
    shift = models.CharField(
        max_length=10,
        choices=ShiftType.choices,
        default=ShiftType.DAY,
        db_index=True
    )
    employee = models.CharField(max_length=100, db_index=True, null=True)

    # 2. Payload (Lưu dưới dạng JSON để linh hoạt theo Form động)
    # Bao gồm: productCode, goodPro, dlnc, scrap...
    production_data = models.JSONField(default=list, blank=True)

    # Bao gồm: stopCode, duration, description...
    stop_time_data = models.JSONField(default=list, blank=True, null=True)

    # 3. Additional Info
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Maris Production Entry"

    def __str__(self):
        # get_shift_display() tự động lấy label 'Day Shift' thay vì 'DAY'
        return f"{self.date} - {self.get_shift_display()} - {self.employee}"