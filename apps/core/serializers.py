class AutoLinksMixin:
    """JSON:API self link를 자동 생성하는 Mixin.

    사용법:
        class PostSerializer(AutoLinksMixin, HookableSerializerMixin, serializers.ModelSerializer):
            resource_path = "posts"
    """

    resource_path = None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.resource_path:
            data.setdefault("links", {})["self"] = f"/api/v1/{self.resource_path}/{instance.pk}"
        return data


class StatusLabelMixin:
    """status_labels_ko dict를 선언하면 get_status_label을 자동 제공."""

    status_labels_ko: dict = {}

    def get_status_label(self, obj):
        return self.status_labels_ko.get(obj.status, obj.get_status_display())
