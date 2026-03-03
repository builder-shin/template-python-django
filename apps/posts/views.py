from apps.core.views import ApiViewSet

from .models import Post


class PostsViewSet(ApiViewSet):

    def create_after_init(self, instance) -> None:
        instance.user = self.request.user

    @property
    def allowed_includes(self):
        return ["comments"]

    def get_base_queryset(self):
        return Post.objects.order_by("-created_at")

    def get_index_scope(self):
        # super()는 mixin 체인(AutoPrefetch + PreloadIncludes)이 적용된 queryset 반환
        return super().get_index_scope().filter(user=self.request.user)

    def upsert_after_init(self, instance):
        if not instance.user_id:
            instance.user = self.request.user

    def upsert_find_params(self):
        body = self._parse_raw_body()
        external_id = body.get("data", {}).get("attributes", {}).get("external_id")
        if not external_id:
            return None
        return {"external_id": external_id}
