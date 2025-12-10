from django.shortcuts import render
from rest_framework import viewsets
from stoptime.models import StopTime
from stoptime.serializers import StopTimeSerializer


class StopTimeViewSet(viewsets.ModelViewSet):
    queryset = StopTime.objects.all().order_by('-stop_time_name')
    serializer_class = StopTimeSerializer
