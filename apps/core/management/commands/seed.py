from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "개발용 샘플 데이터 생성"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="기존 데이터 삭제 후 시드",
        )

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        from apps.comments.models import Comment
        from apps.posts.models import Post
        from tests.factories import CommentFactory, PostFactory, UserFactory

        User = get_user_model()

        if options["flush"]:
            self.stdout.write(">>> 기존 데이터 삭제...")
            Comment.objects.all().delete()
            Post.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING("기존 데이터 삭제 완료"))

        # User 생성
        users = UserFactory.create_batch(10)
        self.stdout.write(f"  User {len(users)}개 생성")

        # Post 생성 (다양한 상태)
        posts = []
        for i, user in enumerate(users[:5]):
            batch = PostFactory.create_batch(
                4,
                user=user,
                status=Post.Status(i % len(Post.Status)),
            )
            posts.extend(batch)
        self.stdout.write(f"  Post {len(posts)}개 생성")

        # Comment 생성
        comments = []
        for post in posts[:10]:
            batch = CommentFactory.create_batch(
                3,
                post=post,
                user=post.user,
            )
            comments.extend(batch)
        self.stdout.write(f"  Comment {len(comments)}개 생성")

        self.stdout.write(self.style.SUCCESS("\n=== 시드 데이터 생성 완료! ==="))
        self.stdout.write(f"  총 User: {User.objects.count()}개")
        self.stdout.write(f"  총 Post: {Post.objects.count()}개")
        self.stdout.write(f"  총 Comment: {Comment.objects.count()}개")
