import factory
from django.conf import settings
from django.db.models import signals
from factory import fuzzy

from accounts.models import CustomerAccount, BankAccount, AccountCurrencyChoices, Transaction, TransactionStatusChoices
from users.tests.factories import UserFactoryNoSignals


@factory.django.mute_signals(signals.post_save)
class BankAccountFactory(factory.DjangoModelFactory):
    balance = factory.Faker('pydecimal', left_digits=4, right_digits=2)
    currency = fuzzy.FuzzyChoice(AccountCurrencyChoices.values, getter=lambda c: c)
    uuid = factory.Faker('uuid4')

    class Meta:
        model = BankAccount


@factory.django.mute_signals(signals.post_save)
class CustomerAccountFactory(factory.DjangoModelFactory):
    balance = factory.Faker('pydecimal', left_digits=4, right_digits=2)
    currency = fuzzy.FuzzyChoice(AccountCurrencyChoices.values, getter=lambda c: c)
    owner = factory.SubFactory(UserFactoryNoSignals)

    class Meta:
        model = CustomerAccount


@factory.django.mute_signals(signals.post_save)
class NewTransactionFactory(factory.DjangoModelFactory):
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, min_value=0)
    fee = factory.LazyAttribute(lambda a: a.amount * settings.COMISSION)
    description = factory.Faker('sentence', nb_words=6)
    from_account = factory.SubFactory(CustomerAccountFactory)
    to_account = factory.SubFactory(CustomerAccountFactory)
    status = fuzzy.FuzzyChoice(TransactionStatusChoices.values, getter=lambda c: c)

    class Meta:
        model = Transaction
