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
        from tests.factories import MemberFactory, PostFactory, CommentFactory
        from apps.comments.models import Comment
        from apps.posts.models import Post
        from apps.members.models import Member

        if options["flush"]:
            self.stdout.write(">>> 기존 데이터 삭제...")
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Member.objects.all().delete()
            self.stdout.write(self.style.WARNING("기존 데이터 삭제 완료"))

        # Member 생성
        members = MemberFactory.create_batch(10)
        self.stdout.write(f"  Member {len(members)}개 생성")

        # Post 생성 (다양한 상태)
        posts = []
        for i, member in enumerate(members[:5]):
            batch = PostFactory.create_batch(
                4,
                user_id=member.user_id,
                status=i % 3,  # draft(0), published(1), archived(2) 순환
            )
            posts.extend(batch)
        self.stdout.write(f"  Post {len(posts)}개 생성")

        # Comment 생성
        comments = []
        for post in posts[:10]:
            batch = CommentFactory.create_batch(
                3,
                post=post,
                user_id=post.user_id,
            )
            comments.extend(batch)
        self.stdout.write(f"  Comment {len(comments)}개 생성")

        self.stdout.write(self.style.SUCCESS("\n=== 시드 데이터 생성 완료! ==="))
        self.stdout.write(f"  총 Member: {Member.objects.count()}개")
        self.stdout.write(f"  총 Post: {Post.objects.count()}개")
        self.stdout.write(f"  총 Comment: {Comment.objects.count()}개")
