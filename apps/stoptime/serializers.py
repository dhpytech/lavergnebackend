from rest_framework import serializers
from stoptime.models import StopTime


class StopTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StopTime
        fields = ['id', 'stop_time_name', 'stop_time_description']
