from rest_framework import serializers
from .models import MarisInput


class MarisInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarisInput
        fields = '__all__'

