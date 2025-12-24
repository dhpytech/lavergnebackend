from rest_framework import serializers
from problems.models import Problem


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'problem_code', 'problem_name']
        