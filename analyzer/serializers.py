from rest_framework import serializers
from .models import StringAnalysis


class StringAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringAnalysis
        fields = ['id', 'value', 'properties', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # remove internal hash from properties
        if "properties" in data and "sha256_hash" in data["properties"]:
            del data["properties"]["sha256_hash"]
            return data
