import pytest
from django.core.exceptions import ValidationError

from tests.factories import CommentFactory, PostFactory


@pytest.mark.django_db
class TestCommentModel:
    def test_create_comment(self, auth_user):
        post = PostFactory(title="Test Post", content="Content", user=auth_user)
        comment = CommentFactory(post=post, content="Nice post!", user=auth_user)
        assert comment.content == "Nice post!"
        assert comment.post_id == post.id
        assert comment.parent is None

    def test_str(self, auth_user):
        comment = CommentFactory(content="Test", user=auth_user)
        assert str(auth_user) in str(comment)

    def test_reply_must_be_same_post(self, auth_user):
        """대댓글은 같은 글의 댓글에만 달 수 있다."""
        post1 = PostFactory(title="Post 1", content="Content", user=auth_user)
        post2 = PostFactory(title="Post 2", content="Content", user=auth_user)
        parent = CommentFactory(post=post1, content="Parent", user=auth_user)
        child = CommentFactory.build(post=post2, parent=parent, content="Child", user=auth_user)
        with pytest.raises(ValidationError) as exc_info:
            child.full_clean()
        assert "parent" in exc_info.value.message_dict
