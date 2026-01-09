from rest_framework import viewsets
from .models import MarisInput, MetalInput, BaggingInput
from .serializers import MarisInputSerializer, MetalInputSerializer, BaggingInputSerializer
from django_filters.rest_framework import DjangoFilterBackend


# 1. Maris ViewSet
class MarisInputViewSet(viewsets.ModelViewSet):
    queryset = MarisInput.objects.all()
    serializer_class = MarisInputSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'date': ['gte', 'lte'],
    }


# 2. Metal ViewSet
class MetalInputViewSet(viewsets.ModelViewSet):
    queryset = MetalInput.objects.all()
    serializer_class = MetalInputSerializer


# 3. Bagging ViewSet
class BaggingInputViewSet(viewsets.ModelViewSet):
    queryset = BaggingInput.objects.all()
    serializer_class = BaggingInputSerializer
