from decimal import Decimal

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import CustomerAccount, AccountCurrencyChoices, Transaction
from accounts.tests.factories import CustomerAccountFactory, NewTransactionFactory
from users.tests.factories import UserFactoryNoSignals


class CustomersTransactionViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.client.force_authenticate(self.customer)

    @classmethod
    def setUpTestData(cls):
        cls.customer = UserFactoryNoSignals(is_staff=False)
        cls.another_customer_account_rub = CustomerAccountFactory(
            owner=UserFactoryNoSignals(is_staff=False),
            currency=AccountCurrencyChoices.RUB,
            balance=Decimal(500),
        )
        cls.customer_account_rub = CustomerAccountFactory(
            owner=cls.customer,
            currency=AccountCurrencyChoices.RUB,
            balance=Decimal(500),
        )
        cls.another_customer_account_usd = CustomerAccountFactory(
            owner=UserFactoryNoSignals(is_staff=False),
            currency=AccountCurrencyChoices.USD,
            balance=Decimal(500),
        )
        cls.customer_account_usd = CustomerAccountFactory(
            owner=cls.customer,
            currency=AccountCurrencyChoices.USD,
            balance=Decimal(500),
        )
        cls.transactions = NewTransactionFactory.create_batch(3)
        cls.customer_transactions = NewTransactionFactory.create_batch(
            3, from_account=cls.customer_account_rub
        )
        cls.own_transaction_detail_url = reverse(
            'accounts:transaction-detail',
            kwargs={'pk': cls.customer_transactions[0].pk}
        )
        cls.another_transaction_detail_url = reverse(
            'accounts:transaction-detail',
            kwargs={'pk': cls.transactions[0].pk}
        )
        cls.list_url = reverse('accounts:transaction-list')

    def test_create_new_same_currency_own_accounts(self):
        data = {
            'from_account': self.customer_account_rub.id,
            'to_account': CustomerAccountFactory(
                owner=self.customer,
                currency=AccountCurrencyChoices.RUB,
                balance=Decimal(100),
            ).id,
            'amount': Decimal(30)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data['fee']), 0)

    def test_create_new_from_not_own_from_account(self):
        data = {
            'from_account': self.another_customer_account_rub.id,
            'to_account': CustomerAccountFactory(
                owner=self.customer,
                currency=AccountCurrencyChoices.EUR,
                balance=Decimal(100),
            ).id,
            'amount': Decimal(30)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_new_different_currency_own_accounts(self):
        data = {
            'from_account': self.customer_account_rub.id,
            'to_account': CustomerAccountFactory(
                owner=self.customer,
                currency=AccountCurrencyChoices.EUR,
                balance=Decimal(100),
            ).id,
            'amount': Decimal(30)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_new_different_currency_to_another_customer(self):
        data = {
            'from_account': self.customer_account_rub.id,
            'to_account': self.another_customer_account_usd.id,
            'amount': Decimal(30)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_new_same_currency_to_another_customer(self):
        data = {
            'from_account': self.customer_account_rub.id,
            'to_account': self.another_customer_account_rub.id,
            'amount': Decimal(30)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_get_transaction_details(self):
        response = self.client.get(self.own_transaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('timestamp', response.data)

    def test_can_get_list_of_transactions(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer_transactions = Transaction.objects.filter(
            from_account__in=CustomerAccount.objects.filter(
                owner=self.customer
            )
        )
        self.assertEqual(
            len(response.data),
            customer_transactions.count()
        )


class StaffUsesCustomerAccountViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = UserFactoryNoSignals(is_staff=True)
        cls.customer = UserFactoryNoSignals(is_staff=False)
        cls.account = CustomerAccountFactory(owner=cls.customer)
        cls.neighbor_account = CustomerAccountFactory(
            owner=UserFactoryNoSignals(is_staff=False)
        )
        cls.detail_url = reverse(
            'accounts:account-detail', kwargs={'pk': cls.account.pk}
        )
        cls.list_url = reverse('accounts:account-list')

    def setUp(self) -> None:
        self.client.force_authenticate(self.staff_user)

    def test_staff_user_can_access_any_account(self):
        CustomerAccountFactory.create_batch(3, owner=self.staff_user)

        response = self.client.get(self.list_url)
        self.assertEqual(
            CustomerAccount.objects.all().count(),
            len(response.data)
        )

    def test_staff_user_can_not_modify_account(self):
        data = {
            'currency': AccountCurrencyChoices.EUR,
            'balance': Decimal(200),
        }
        url = reverse(
            'accounts:account-detail', kwargs={'pk': self.account.pk}
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CustomerAccountViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.client.force_authenticate(self.customer)

    @classmethod
    def setUpTestData(cls):
        cls.customer = UserFactoryNoSignals(is_staff=False)
        cls.account = CustomerAccountFactory(
            owner=cls.customer,
            currency=AccountCurrencyChoices.RUB,
            balance=Decimal(100)
        )
        cls.another_customer_account = CustomerAccountFactory(
            owner=UserFactoryNoSignals(is_staff=False)
        )
        cls.detail_url = reverse(
            'accounts:account-detail', kwargs={'pk': cls.account.pk}
        )
        cls.list_url = reverse('accounts:account-list')

    def test_customer_can_create_new_account(self):
        data = {
            'currency': AccountCurrencyChoices.RUB
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_account_details_can_be_retrieved_by_owner(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.account.balance,
            Decimal(response.data['balance'])
        )
        self.assertEqual(self.account.currency, response.data['currency'])

    def test_customer_can_retrieve_list_of_own_accounts(self):
        CustomerAccountFactory.create_batch(3, owner=self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(
            CustomerAccount.objects.filter(owner=self.customer).count(),
            len(response.data)
        )
        self.assertNotIn(
            self.another_customer_account.id,
            [item['id'] for item in response.data]
        )

    def test_user_can_not_patch_account(self):
        data = {
            'currency': AccountCurrencyChoices.EUR
        }
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_can_not_put_account(self):
        data = {
            'currency': AccountCurrencyChoices.EUR,
            'balance': Decimal(100),
        }
        response = self.client.patch(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_can_not_delete_account(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_can_not_read_another_customer_account(self):
        url = reverse(
            'accounts:account-detail', kwargs={'pk': self.another_customer_account.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_not_modify_another_customer_account(self):
        data = {
            'currency': AccountCurrencyChoices.EUR,
            'balance': Decimal(100),
        }
        url = reverse(
            'accounts:account-detail', kwargs={'pk': self.another_customer_account.pk}
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
