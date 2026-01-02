from rest_framework import serializers
from dlnc_case.models import DlncCase


class DlncCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DlncCase
        fields = ['dlnc_case_name', 'dlnc_case_description']
