from rest_framework import viewsets
from .models import SafetyTime
from .serializers import SafetyTimeSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
# Đảm bảo bạn đã import model SafetyTime từ cùng ứng dụng
from .models import SafetyTime


class SafetyTimeViewSet(viewsets.ModelViewSet):
    queryset = SafetyTime.objects.all().order_by('-safety_date')
    serializer_class = SafetyTimeSerializer


class SafetyDurationView(APIView):
    def get(self, request):
        # 1. Lấy thời gian hiện tại (aware datetime)
        now = timezone.now()

        latest_event = SafetyTime.objects.filter(safety_date__lte=now).order_by('-safety_date').first()

        if not latest_event:
            print('Sai rôi')
            return Response(
                {"message": "Chưa có dữ liệu về sự kiện an toàn nào được ghi nhận."},
                status=status.HTTP_404_NOT_FOUND
            )
        duration = now - latest_event.safety_date
        total_seconds = int(duration.total_seconds())
        days = duration.days
        seconds_remainder = duration.seconds
        hours = seconds_remainder // 3600
        minutes = (seconds_remainder % 3600) // 60
        seconds = seconds_remainder % 60

        data = {
            "last_safety_date": latest_event.safety_date,
            "safety_type": latest_event.get_safety_type_display(),
            "description_snippet": latest_event.safety_description[:50] + "...",  # Lấy 50 ký tự đầu
            "duration_since": {
                "days": days,
                "hours": days*24 + hours,
                "minutes": minutes,
                "seconds": seconds,
                "total_seconds": total_seconds
            },
            "formatted_time": f"{days*24 + hours:02d} hours: {minutes:02d} minutes"
        }
        return Response(data, status=status.HTTP_200_OK)
