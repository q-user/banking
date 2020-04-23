import uuid
from decimal import Decimal

from django.db import models, transaction
from django.db.models import deletion, F
from polymorphic.models import PolymorphicModel

from accounts.transactions import InsufficientFundsException
from users.models import User


class AccountCurrencyChoices(models.TextChoices):
    USD = 'USD'
    RUB = 'RUB'
    EUR = 'EUR'


class Account(PolymorphicModel):
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Баланс',
    )
    currency = models.CharField(
        max_length=4,
        choices=AccountCurrencyChoices.choices,
        verbose_name='Валюта счёта'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Счёт'
        verbose_name_plural = 'Счета'


class BankAccount(Account):
    uuid = models.UUIDField(default=uuid.uuid4)

    class Meta:
        verbose_name = 'Счёт банка'
        verbose_name_plural = 'Счёта банка'

    def __str__(self):
        return f'Bank\'s account - {self.balance} {self.currency}'


class CustomerAccount(Account):
    owner = models.ForeignKey(User, on_delete=deletion.CASCADE, related_name='accounts')

    class Meta:
        verbose_name = 'Счёт клиента'
        verbose_name_plural = 'Счета клиентов'

    def __str__(self):
        return f'{self.currency} account of {self.owner}'


class TransactionStatusChoices(models.IntegerChoices):
    PENDING = 0
    SUCCESS = 1
    ERROR = 2


class Transaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Сумма')
    fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        verbose_name='Комиссия'
    )
    new_from_balance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        verbose_name='Новый баланс'
    )
    new_to_balance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        verbose_name='Новый баланс'
    )
    description = models.CharField(max_length=250, verbose_name='Примечание')
    from_account = models.ForeignKey(
        Account,
        on_delete=deletion.CASCADE,
        verbose_name='Счет отправитель',
        related_name='outbound_transations',
    )
    to_account = models.ForeignKey(
        Account,
        on_delete=deletion.CASCADE,
        verbose_name='Счет получатель',
        related_name='inbound_transations',
    )
    status = models.PositiveSmallIntegerField(
        choices=TransactionStatusChoices.choices,
        default=TransactionStatusChoices.PENDING
    )
    error_msg = models.CharField(max_length=250, verbose_name='Причина отклонения')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def commit(self):
        amount = Decimal(self.amount)
        fee = Decimal(self.fee)
        from_balance = Decimal(self.from_account.balance, )
        to_balance = Decimal(self.to_account.balance)
        total = amount + fee
        new_from_balance = from_balance - total
        new_to_balance = to_balance + amount

        if from_balance - total < 0:
            msg = f'Недостаточно средств на балансе.' \
                  f' Запрашиваемая сумма {total}, остаток на балансе {total}.'
            self.error_msg = msg
            self.status = TransactionStatusChoices.ERROR
            self.save()
            raise InsufficientFundsException(msg)

        with transaction.atomic():
            Account.objects.filter(
                id=self.to_account.id
            ).update(
                balance=new_to_balance
            )
            Account.objects.filter(
                id=self.from_account.id
            ).update(
                balance=new_from_balance
            )

            if fee > 0:
                BankAccount.objects.filter(
                    currency=self.from_account.currency
                ).update(balance=F('balance') + fee)

            self.status = TransactionStatusChoices.SUCCESS
            self.new_from_balance = new_from_balance
            self.new_to_balance = new_to_balance
            self.save()
