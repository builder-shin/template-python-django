import pytest

from apps.comments.models import Comment
from apps.posts.models import Post


@pytest.mark.django_db
class TestCommentModel:
    def test_create_comment(self, member):
        post = Post.objects.create(title="Test Post", content="Content", member=member)
        comment = Comment.objects.create(post=post, content="Nice post!", member=member)
        assert comment.content == "Nice post!"
        assert comment.post_id == post.id
        assert comment.parent is None

    def test_str(self, member):
        post = Post.objects.create(title="Test Post", content="Content", member=member)
        comment = Comment.objects.create(post=post, content="Test", member=member)
        assert str(member) in str(comment)
