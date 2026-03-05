from rest_framework_json_api import serializers

from apps.core.mixins.crud_actions import HookableSerializerMixin

from .models import User


class UserSerializer(HookableSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "nickname",
            "bio",
            "avatar_url",
            "status",
            "date_joined",
        ]
        read_only_fields = ["date_joined", "status"]
