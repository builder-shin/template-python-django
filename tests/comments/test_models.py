import pytest

from apps.posts.models import Post
from apps.comments.models import Comment


@pytest.mark.django_db
class TestCommentModel:
    def test_create_comment(self):
        post = Post.objects.create(title="Test Post", content="Content", user_id="user-1")
        comment = Comment.objects.create(post=post, content="Nice post!", user_id="user-2")
        assert comment.content == "Nice post!"
        assert comment.post_id == post.id
        assert comment.parent is None

    def test_is_reply(self):
        post = Post.objects.create(title="Test Post", content="Content", user_id="user-1")
        parent = Comment.objects.create(post=post, content="Parent", user_id="user-2")
        reply = Comment.objects.create(post=post, content="Reply", user_id="user-3", parent=parent)
        assert parent.is_reply() is False
        assert reply.is_reply() is True

    def test_reply_count(self):
        post = Post.objects.create(title="Test Post", content="Content", user_id="user-1")
        parent = Comment.objects.create(post=post, content="Parent", user_id="user-2")
        Comment.objects.create(post=post, content="Reply 1", user_id="user-3", parent=parent)
        Comment.objects.create(post=post, content="Reply 2", user_id="user-4", parent=parent)
        assert parent.reply_count() == 2

    def test_author_name(self):
        comment = Comment(user_id="user-1")
        assert comment.author_name() == "User#user-1"

    def test_str(self):
        post = Post.objects.create(title="Test Post", content="Content", user_id="user-1")
        comment = Comment.objects.create(post=post, content="Test", user_id="user-2")
        assert "user-2" in str(comment)


@pytest.mark.django_db
class TestCommentQuerySet:
    def test_by_post(self):
        p1 = Post.objects.create(title="Post 1", content="c", user_id="u1")
        p2 = Post.objects.create(title="Post 2", content="c", user_id="u1")
        Comment.objects.create(post=p1, content="C1", user_id="u2")
        Comment.objects.create(post=p2, content="C2", user_id="u2")
        assert Comment.objects.by_post(p1.id).count() == 1

    def test_by_user(self):
        post = Post.objects.create(title="Post", content="c", user_id="u1")
        Comment.objects.create(post=post, content="C1", user_id="u2")
        Comment.objects.create(post=post, content="C2", user_id="u3")
        assert Comment.objects.by_user("u2").count() == 1

    def test_root_comments(self):
        post = Post.objects.create(title="Post", content="c", user_id="u1")
        parent = Comment.objects.create(post=post, content="Root", user_id="u2")
        Comment.objects.create(post=post, content="Reply", user_id="u3", parent=parent)
        assert Comment.objects.root_comments().count() == 1

    def test_recent(self):
        post = Post.objects.create(title="Post", content="c", user_id="u1")
        c1 = Comment.objects.create(post=post, content="First", user_id="u2")
        c2 = Comment.objects.create(post=post, content="Second", user_id="u3")
        results = list(Comment.objects.recent())
        assert results[0].pk == c2.pk
