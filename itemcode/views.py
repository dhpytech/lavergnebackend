from rest_framework import viewsets
from itemcode.models import ItemCode
from itemcode.serializers import ItemCodeSerializer


class ItemCodeViewSet(viewsets.ModelViewSet):
    queryset = ItemCode.objects.all().order_by('-item_name')
    serializer_class = ItemCodeSerializer
