import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker("ko_KR")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = "users.User"

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    nickname = factory.LazyFunction(lambda: fake.name())
    status = 0  # active


class PostFactory(DjangoModelFactory):
    class Meta:
        model = "posts.Post"

    title = factory.LazyFunction(lambda: fake.sentence())
    content = factory.LazyFunction(lambda: fake.paragraph())
    user = factory.SubFactory(UserFactory)
    status = 0  # draft


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = "comments.Comment"

    content = factory.LazyFunction(lambda: fake.sentence())
    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)
