from rest_framework import serializers
from .models import TenNhanVien


class TenNhanVienSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenNhanVien
        fields = ['id', 'name']
