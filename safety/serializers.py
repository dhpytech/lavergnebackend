from rest_framework import serializers
from .models import SafetyTime


class SafetyTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyTime
        fields = ['id', 'safety_date', 'safety_type', 'safety_description']
