import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.posts.models import Post
from tests.factories import PostFactory


@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self, auth_user):
        post = PostFactory(title="Test Post", content="Content", user=auth_user)
        assert post.title == "Test Post"
        assert post.status == Post.Status.DRAFT
        assert post.view_count == 0

    def test_strip_title(self, auth_user):
        post = PostFactory(title="  spaces  ", content="Content", user=auth_user)
        assert post.title == "spaces"

    def test_published_with_future_date_raises(self, auth_user):
        """발행 상태에서 미래 published_at → ValidationError."""
        post = PostFactory.build(
            title="Future",
            content="Content",
            user=auth_user,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now() + timezone.timedelta(days=1),
        )
        with pytest.raises(ValidationError) as exc_info:
            post.full_clean()
        assert "published_at" in exc_info.value.message_dict

    def test_published_without_content_raises(self, auth_user):
        """발행 상태에서 content 없음 → ValidationError."""
        post = PostFactory.build(
            title="No Content",
            content="",
            user=auth_user,
            status=Post.Status.PUBLISHED,
        )
        with pytest.raises(ValidationError) as exc_info:
            post.full_clean()
        assert "content" in exc_info.value.message_dict
