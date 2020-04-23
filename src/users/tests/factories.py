import factory
from django.db.models import signals

from users.models import User


@factory.django.mute_signals(signals.post_save)
class UserFactoryNoSignals(factory.DjangoModelFactory):
    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_staff = factory.Faker('pybool')

    class Meta:
        model = User


class UserFactory(factory.DjangoModelFactory):
    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_staff = factory.Faker('pybool')

    class Meta:
        model = User
