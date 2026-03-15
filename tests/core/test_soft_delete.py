"""SoftDeleteMixin 통합 테스트 — Phase 1~4 TDD.

실제 모델(Post, Comment)을 사용하여 테스트한다.
"""

import pytest
from django.utils import timezone

from apps.comments.models import Comment
from apps.posts.models import Post
from tests.factories import CommentFactory, PostFactory, UserFactory

pytestmark = pytest.mark.django_db


# ===========================================================================
# Phase 1: SoftDeleteQuerySet + SoftDeleteManager
# ===========================================================================


class TestSoftDeleteQuerySet:
    def test_default_queryset_excludes_soft_deleted(self):
        user = UserFactory()
        alive = PostFactory(user=user)
        deleted = PostFactory(user=user)
        deleted.deleted_at = timezone.now()
        deleted.save(update_fields=["deleted_at"])

        qs = Post.objects.all()
        assert alive in qs
        assert deleted not in qs

    def test_alive_returns_only_non_deleted(self):
        user = UserFactory()
        alive = PostFactory(user=user)
        deleted = PostFactory(user=user)
        deleted.deleted_at = timezone.now()
        deleted.save(update_fields=["deleted_at"])

        qs = Post.objects.alive()
        assert alive in qs
        assert deleted not in qs

    def test_dead_returns_only_deleted(self):
        user = UserFactory()
        alive = PostFactory(user=user)
        deleted = PostFactory(user=user)
        deleted.deleted_at = timezone.now()
        deleted.save(update_fields=["deleted_at"])

        qs = Post.objects.dead()
        assert alive not in qs
        assert deleted in qs

    def test_all_with_deleted_includes_everything(self):
        user = UserFactory()
        alive = PostFactory(user=user)
        deleted = PostFactory(user=user)
        deleted.deleted_at = timezone.now()
        deleted.save(update_fields=["deleted_at"])

        qs = Post.all_objects.all()
        assert alive in qs
        assert deleted in qs

    def test_queryset_delete_performs_soft_delete(self):
        user = UserFactory()
        PostFactory(user=user)
        PostFactory(user=user)

        result = Post.objects.filter(user=user).delete()

        assert result[0] == 2  # Django delete() 반환값 계약: (count, {label: count})
        assert Post.objects.filter(user=user).count() == 0
        assert Post.all_objects.filter(user=user).count() == 2
        assert Post.all_objects.filter(user=user, deleted_at__isnull=False).count() == 2

    def test_queryset_bulk_delete_does_not_cascade(self):
        """Bulk soft delete는 cascade를 적용하지 않는다."""
        user = UserFactory()
        post = PostFactory(user=user)
        CommentFactory(post=post, user=user)

        Post.objects.filter(user=user).delete()

        assert Comment.objects.filter(post=post).count() == 1  # Comment는 alive

    def test_queryset_hard_delete_performs_physical_delete(self):
        user = UserFactory()
        PostFactory(user=user)
        PostFactory(user=user)

        Post.objects.filter(user=user).hard_delete()

        assert Post.all_objects.filter(user=user).count() == 0


# ===========================================================================
# Phase 2: SoftDeleteMixin 핵심 (delete / restore)
# ===========================================================================


class TestSoftDeleteMixin:
    def test_soft_delete_sets_deleted_at(self):
        post = PostFactory()
        post.delete()

        post.refresh_from_db()
        assert post.deleted_at is not None

    def test_soft_delete_does_not_remove_from_db(self):
        post = PostFactory()
        pk = post.pk
        post.delete()

        assert Post.all_objects.filter(pk=pk).exists()

    def test_hard_delete_removes_from_db(self):
        post = PostFactory()
        pk = post.pk
        post.delete(hard_delete=True)

        assert not Post.all_objects.filter(pk=pk).exists()

    def test_restore_clears_deleted_at(self):
        post = PostFactory()
        post.delete()
        post.refresh_from_db()
        assert post.deleted_at is not None

        post.restore()
        post.refresh_from_db()
        assert post.deleted_at is None

    def test_restore_already_alive_is_noop(self):
        post = PostFactory()
        post.restore()  # should not raise
        post.refresh_from_db()
        assert post.deleted_at is None

    def test_is_deleted_property(self):
        post = PostFactory()
        assert post.is_deleted is False

        post.delete()
        post.refresh_from_db()
        assert post.is_deleted is True


# ===========================================================================
# Phase 3: 커스텀 on_delete 캐스케이드 핸들러
# ===========================================================================


class TestSoftCascade:
    """SOFT_CASCADE: Post soft delete → Comment soft delete."""

    def test_soft_cascade_parent_soft_deletes_children(self):
        post = PostFactory()
        c1 = CommentFactory(post=post, user=post.user)
        c2 = CommentFactory(post=post, user=post.user)

        post.delete()

        c1.refresh_from_db()
        c2.refresh_from_db()
        assert c1.is_deleted is True
        assert c2.is_deleted is True

    def test_soft_cascade_parent_restore_restores_children(self):
        post = PostFactory()
        c1 = CommentFactory(post=post, user=post.user)
        c2 = CommentFactory(post=post, user=post.user)

        post.delete()
        post.refresh_from_db()
        post.restore()

        c1.refresh_from_db()
        c2.refresh_from_db()
        assert c1.is_deleted is False
        assert c2.is_deleted is False


class TestHardCascadeSoftChildren:
    """HARD_CASCADE_SOFT_CHILDREN: Comment.parent hard delete → 대댓글 soft delete (nullable FK)."""

    def test_hard_cascade_soft_children_nullable_fk(self):
        post = PostFactory()
        parent_comment = CommentFactory(post=post, user=post.user)
        reply = CommentFactory(post=post, user=post.user, parent=parent_comment)

        parent_comment.delete(hard_delete=True)

        assert not Comment.all_objects.filter(pk=parent_comment.pk).exists()
        reply.refresh_from_db()
        assert reply.is_deleted is True
        assert reply.parent_id is None


class TestSoftCascadePostComments:
    """Post soft delete 시 Comment도 soft delete (SOFT_CASCADE)."""

    def test_post_soft_delete_cascades_to_comments(self):
        post = PostFactory()
        comment = CommentFactory(post=post, user=post.user)
        reply = CommentFactory(post=post, user=post.user, parent=comment)

        post.delete()

        comment.refresh_from_db()
        reply.refresh_from_db()
        assert comment.is_deleted is True
        assert reply.is_deleted is True


class TestSelfReferentialCascade:
    """Comment self-FK 에서 무한재귀 없이 동작."""

    def test_self_referential_cascade_no_infinite_loop(self):
        post = PostFactory()
        root = CommentFactory(post=post, user=post.user)
        child = CommentFactory(post=post, user=post.user, parent=root)
        grandchild = CommentFactory(post=post, user=post.user, parent=child)

        # Post soft delete → 모든 Comment soft delete (SOFT_CASCADE)
        post.delete()

        root.refresh_from_db()
        child.refresh_from_db()
        grandchild.refresh_from_db()
        assert root.is_deleted is True
        assert child.is_deleted is True
        assert grandchild.is_deleted is True


class TestCascadePerFKPolicy:
    """동일 모델(Comment)의 서로 다른 FK에 서로 다른 정책 적용."""

    def test_cascade_respects_per_fk_policy(self):
        post = PostFactory()
        parent_comment = CommentFactory(post=post, user=post.user)
        reply = CommentFactory(post=post, user=post.user, parent=parent_comment)

        # Post soft delete → Comment soft delete (SOFT_CASCADE on "post" FK)
        post.delete()

        parent_comment.refresh_from_db()
        reply.refresh_from_db()
        assert parent_comment.is_deleted is True
        assert reply.is_deleted is True  # cascaded through post FK


# ===========================================================================
# Phase 4: Post/Comment 모델 적용
# ===========================================================================


class TestCascadeRestoreProtection:
    """deleted_by_cascade 플래그를 통한 복원 보호."""

    def test_cascade_deleted_child_has_deleted_by_cascade_true(self):
        post = PostFactory()
        comment = CommentFactory(post=post, user=post.user)

        post.delete()

        comment.refresh_from_db()
        assert comment.deleted_by_cascade is True

    def test_individually_deleted_child_has_deleted_by_cascade_false(self):
        post = PostFactory()
        comment = CommentFactory(post=post, user=post.user)

        comment.delete()

        comment.refresh_from_db()
        assert comment.deleted_by_cascade is False

    def test_restore_parent_only_restores_cascade_deleted_children(self):
        post = PostFactory()
        cascade_comment = CommentFactory(post=post, user=post.user, content="cascade")
        individual_comment = CommentFactory(post=post, user=post.user, content="individual")

        # 개별 삭제
        individual_comment.delete()

        # 부모 삭제 (cascade_comment도 cascade 삭제됨)
        post.delete()

        # 부모 복원
        post.refresh_from_db()
        post.restore()

        cascade_comment.refresh_from_db()
        individual_comment.refresh_from_db()

        assert cascade_comment.is_deleted is False  # cascade 삭제 → 복원됨
        assert individual_comment.is_deleted is True  # 개별 삭제 → 복원 안 됨

    def test_restored_child_has_deleted_by_cascade_reset_to_false(self):
        post = PostFactory()
        comment = CommentFactory(post=post, user=post.user)

        post.delete()
        post.refresh_from_db()
        post.restore()

        comment.refresh_from_db()
        assert comment.deleted_by_cascade is False

    def test_bulk_queryset_delete_does_not_set_deleted_by_cascade(self):
        user = UserFactory()
        PostFactory(user=user)

        Post.objects.filter(user=user).delete()

        post = Post.all_objects.filter(user=user).first()
        assert post.deleted_by_cascade is False


class TestPostModelIntegration:
    def test_post_default_queryset_excludes_deleted(self):
        post = PostFactory()
        post.delete()

        assert Post.objects.filter(pk=post.pk).exists() is False
        assert Post.all_objects.filter(pk=post.pk).exists() is True

    def test_post_unique_constraint_with_soft_delete(self):
        """Soft-deleted Post는 unique constraint에서 제외."""
        user = UserFactory()
        post1 = PostFactory(title="unique title", user=user)
        post1.delete()

        # 같은 title+user로 새 Post 생성 가능해야 함
        post2 = PostFactory(title="unique title", user=user)
        assert post2.pk is not None
        assert post2.pk != post1.pk


class TestCommentModelIntegration:
    def test_comment_soft_delete_cascade_from_post(self):
        post = PostFactory()
        comment = CommentFactory(post=post, user=post.user)

        post.delete()

        comment.refresh_from_db()
        assert comment.is_deleted is True

    def test_comment_parent_hard_cascade_soft_children(self):
        """Comment.parent(nullable FK) hard delete → 대댓글 soft delete."""
        post = PostFactory()
        parent = CommentFactory(post=post, user=post.user)
        reply = CommentFactory(post=post, user=post.user, parent=parent)

        parent.delete(hard_delete=True)

        reply.refresh_from_db()
        assert reply.is_deleted is True
        assert reply.parent_id is None
