import uuid

import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker("ko_KR")


class MemberFactory(DjangoModelFactory):
    class Meta:
        model = "members.Member"

    nickname = factory.LazyFunction(lambda: fake.name())
    user_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    status = 0  # active


class PostFactory(DjangoModelFactory):
    class Meta:
        model = "posts.Post"

    title = factory.LazyFunction(lambda: fake.sentence())
    content = factory.LazyFunction(lambda: fake.paragraph())
    user_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    status = 0  # draft


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = "comments.Comment"

    content = factory.LazyFunction(lambda: fake.sentence())
    post = factory.SubFactory(PostFactory)
    user_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
