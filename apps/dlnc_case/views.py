from django.shortcuts import render
from rest_framework import viewsets
from dlnc_case.models import DlncCase
from dlnc_case.serializers import DlncCaseSerializer


# Create your views here.
class DlncCaseViewSet(viewsets.ModelViewSet):
    queryset = DlncCase.objects.all().order_by('-dlnc_case_name')
    serializer_class = DlncCaseSerializer
    