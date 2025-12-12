from django.shortcuts import render
from rest_framework import viewsets
from problems.models import Problem
from problems.serializers import ProblemSerializer


# Create your views here.
class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all().order_by('-problem_code')
    serializer_class = ProblemSerializer
