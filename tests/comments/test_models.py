import pytest

from apps.comments.models import Comment
from apps.posts.models import Post


@pytest.mark.django_db
class TestCommentModel:
    def test_create_comment(self, auth_user):
        post = Post.objects.create(title="Test Post", content="Content", user=auth_user)
        comment = Comment.objects.create(post=post, content="Nice post!", user=auth_user)
        assert comment.content == "Nice post!"
        assert comment.post_id == post.id
        assert comment.parent is None

    def test_str(self, auth_user):
        post = Post.objects.create(title="Test Post", content="Content", user=auth_user)
        comment = Comment.objects.create(post=post, content="Test", user=auth_user)
        assert str(auth_user) in str(comment)
