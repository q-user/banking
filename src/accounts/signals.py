from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomerAccount, AccountCurrencyChoices, Transaction, BankAccount
from accounts.tasks import delay_transaction_commit
from users.models import User


@receiver(post_save, sender=User)
def create_start_accounts_for_new_user(sender, instance, created, **kwargs):
    user = instance
    if created:
        for currency in AccountCurrencyChoices.values:
            CustomerAccount.objects.create(
                owner=user,
                currency=currency
            )

        bank_account = BankAccount.objects.filter(
            currency=AccountCurrencyChoices.USD,
            balance__gt=Decimal(0)
        ).first()

        transaction = Transaction.objects.create(
            amount=Decimal(100.00),
            fee=Decimal(0.00),
            description='Бонус зарегистрировавшемуся участнику.',
            to_account=user.accounts.filter(currency=AccountCurrencyChoices.USD).first(),
            from_account=bank_account
        )
        delay_transaction_commit(transaction)
