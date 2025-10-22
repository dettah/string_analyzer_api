from rest_framework import serializers
from .models import StringAnalysis

class StringAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringAnalysis
        fields = ['id', 'value', 'properties', 'created_at']
        read_only_fields = ['id', 'properties', 'created_at']