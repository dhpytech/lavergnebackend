from safety.models import SafetyTime
from datetime import date


class SafetyService:
    @staticmethod
    def get_summary(start_date, end_date):
        """
        Tính toán tóm tắt an toàn dựa trên Model SafetyTime.
        start_date/end_date có thể là string (YYYY-MM-DD) hoặc object date.
        """

        # 1. Sửa 'incident_date' thành 'safety_date'
        # Sử dụng __date để đảm bảo so sánh chính xác với DateTimeField
        qs = SafetyTime.objects.filter(safety_date__date__range=(start_date, end_date))

        # 2. Sửa 'type' thành 'safety_type'
        # Khớp với vế trái của SAFETY_EVENT_TYPES trong Model
        accident_count = qs.filter(safety_type='accident').count()
        incident_count = qs.filter(safety_type='incident').count()

        # 3. Tính số ngày an toàn (Days without accident)
        # Truy vấn toàn bộ lịch sử để tìm vụ tai nạn cuối cùng
        last_accident = SafetyTime.objects.filter(
            safety_type='accident'
        ).order_by('-safety_date').first()

        days_safe = 0
        if last_accident:
            # last_accident.safety_date là DateTime, cần .date() để trừ với date.today()
            days_safe = (date.today() - last_accident.safety_date.date()).days
        else:
            # Nếu chưa từng có tai nạn, có thể trả về 365 ngày hoặc một mốc cố định
            days_safe = 365

        return {
            "incident": incident_count,
            "accident": accident_count,
            "days_safe": days_safe
        }
