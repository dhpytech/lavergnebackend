from rest_framework import serializers
from itemcode.models import ItemCode


class ItemCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCode
        fields = ['id', 'item_name', 'item_description', 'item_type']
