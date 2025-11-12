from rest_framework import viewsets
from .models import SafetyTime
from .serializers import SafetyTimeSerializer


class SafetyTimeViewSet(viewsets.ModelViewSet):
    queryset = SafetyTime.objects.all().order_by('-safety_date')
    serializer_class = SafetyTimeSerializer
