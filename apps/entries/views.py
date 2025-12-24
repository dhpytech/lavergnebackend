from rest_framework import viewsets
from .models import MarisInput
from .serializers import MarisInputSerializer


class MarisInputViewSet(viewsets.ModelViewSet):
    queryset = MarisInput.objects.all()
    serializer_class = MarisInputSerializer

