from decimal import Decimal

from django.test import TestCase

from accounts.models import Transaction, TransactionStatusChoices
from accounts.tests.factories import NewTransactionFactory, CustomerAccountFactory
from accounts.transactions import InsufficientFundsException


class TransactionModelTest(TestCase):
    def test_transfer_with_insufficient_funds(self):
        from_account = CustomerAccountFactory(
            balance=Decimal(10),
        )
        transaction = NewTransactionFactory(
            amount=Decimal(60),
            from_account=from_account,
            status=TransactionStatusChoices.PENDING,
        )
        with self.assertRaises(InsufficientFundsException):
            transaction.commit()
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionStatusChoices.ERROR)

    def test_success_transfer(self):
        from_account = CustomerAccountFactory(
            balance=Decimal(60),
        )
        transaction = NewTransactionFactory(
            amount=Decimal(10),
            from_account=from_account,
            status=TransactionStatusChoices.PENDING,
        )
        transaction.commit()
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionStatusChoices.SUCCESS)
