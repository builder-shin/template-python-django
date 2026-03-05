from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    """응답 전용 -- Swagger/drf-spectacular 문서화용."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
