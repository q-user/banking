from unittest import mock

from django.test import TestCase

from accounts.models import Transaction
from accounts.tasks import commit_transaction_task
from accounts.tests.factories import NewTransactionFactory


class CommitTransactionTaskTest(TestCase):
    @mock.patch.object(Transaction, 'commit')
    def test_task_calls_transaction_commit_method(self, mock_commit):
        commit_transaction_task(
            NewTransactionFactory().id
        )
        mock_commit.assert_called()
