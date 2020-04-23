from decimal import Decimal
from unittest import mock

from apscheduler.schedulers.background import BackgroundScheduler
from django.test import TestCase

from accounts.models import AccountCurrencyChoices, Transaction
from users.tests.factories import UserFactory


class CreateStartAccountsForNewUserTest(TestCase):
    @mock.patch.object(BackgroundScheduler, 'start')
    def test_every_type_of_account_is_created_on_new_user(self, mock_start):
        customer = UserFactory(is_staff=False)
        self.assertEqual(
            customer.accounts.filter(currency=AccountCurrencyChoices.USD).count(),
            1
        )
        self.assertEqual(
            customer.accounts.filter(currency=AccountCurrencyChoices.EUR).count(),
            1
        )
        self.assertEqual(
            customer.accounts.filter(currency=AccountCurrencyChoices.RUB).count(),
            1
        )

    @mock.patch.object(BackgroundScheduler, 'start')
    def test_there_is_100_dollar_inbound_transaction_for_new_user(self, mock_start):
        customer = UserFactory(is_staff=False)
        usd_account = customer.accounts.filter(currency=AccountCurrencyChoices.USD).first()
        self.assertTrue(
            Transaction.objects.filter(
                amount=Decimal(100.00),
                to_account=usd_account
            ).exists()
        )

    @mock.patch('accounts.tasks.commit_transaction_task')
    def test_transaction_commit_task_run(self, task_mock):
        customer = UserFactory(is_staff=False)
        task_mock.assert_called()
