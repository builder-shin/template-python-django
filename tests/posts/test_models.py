import pytest

from apps.posts.models import Post


@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self, member):
        post = Post.objects.create(title="Test Post", content="Content", member=member)
        assert post.title == "Test Post"
        assert post.status == Post.Status.DRAFT
        assert post.view_count == 0

    def test_strip_title(self, member):
        post = Post.objects.create(title="  spaces  ", content="Content", member=member)
        assert post.title == "spaces"
