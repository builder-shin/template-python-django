import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker("ko_KR")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = "users.User"
        exclude = ["raw_password"]

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    raw_password = "testpass123"
    nickname = factory.LazyFunction(lambda: fake.name())
    status = 0  # active

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        raw_password = kwargs.pop("raw_password", "testpass123")
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, password=raw_password, **kwargs)


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
