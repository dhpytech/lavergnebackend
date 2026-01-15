# File: apps/dashboards/services/safety_services.py
from entries.models import SafetyTime  # Đảm bảo import đúng class SafetyTime
from datetime import date


class SafetyService:
    @staticmethod
    def get_summary(start_date_str, end_date_str):
        # 1. Sửa 'incident_date' thành 'safety_date'
        # Dùng __date để so sánh DateTimeField với chuỗi Date ISO
        qs = SafetyTime.objects.filter(
            safety_date__date__range=(start_date_str, end_date_str)
        )

        # 2. Đếm số vụ (Khớp với choices: 'accident', 'incident')
        accident_count = qs.filter(safety_type__iexact="accident").count()
        incident_count = qs.filter(safety_type__iexact="incident").count()

        # 3. Tính số ngày an toàn (Days without accident)
        # Lấy vụ tai nạn gần nhất trong lịch sử
        last_accident = SafetyTime.objects.filter(
            safety_type__iexact="accident"
        ).order_by('-safety_date').first()

        days_safe = 0
        if last_accident:
            # Tính khoảng cách từ ngày đó đến hôm nay
            delta = date.today() - last_accident.safety_date.date()
            days_safe = delta.days
        else:
            # Nếu chưa từng có tai nạn, trả về một con số tượng trưng
            days_safe = 365

        return {
            "accident": accident_count,
            "incident": incident_count,
            "days_safe": days_safe
        }
