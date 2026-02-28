from rest_framework_json_api import serializers


class ApplicationSerializer(serializers.ModelSerializer):
    """Base serializer for all JSON:API serializers in the project."""

    class Meta:
        abstract = True
