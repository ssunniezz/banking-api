from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Account, Transaction
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()  # Use the custom user model


class AccountTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.account1 = Account.objects.create(user=self.user1, balance=Decimal('100.00'))
        self.account2 = Account.objects.create(user=self.user2, balance=Decimal('200.00'))
        self.client = APIClient()

        # Obtain JWT tokens for authentication
        self.refresh_token = RefreshToken.for_user(self.user1)
        self.access_token = self.refresh_token.access_token

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_account(self):
        data = {
            'user': self.user1.id,
            'balance': '150.00'
        }
        response = self.client.post(reverse('account-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 3)

    def test_retrieve_accounts(self):
        response = self.client.get(reverse('account-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_account(self):
        data = {
            'balance': '300.00'
        }
        response = self.client.patch(reverse('account-detail', kwargs={'pk': self.account1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('300.00'))

    def test_delete_account_with_referenced_transactions(self):
        # Create a transaction
        Transaction.objects.create(account=self.account1, to_account=self.account2, amount=Decimal('50.00'), transaction_type='transfer')

        response = self.client.delete(reverse('account-detail', kwargs={'pk': self.account2.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # value in to_account column changed to null
        self.assertEqual(Transaction.objects.filter(to_account=self.account2.id).count(), 0)

        response = self.client.delete(reverse('account-detail', kwargs={'pk': self.account1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # transaction is deleted
        self.assertEqual(Transaction.objects.filter(to_account=self.account1.id).count(), 0)

    def test_delete_account(self):
        response = self.client.delete(reverse('account-detail', kwargs={'pk': self.account1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Account.objects.filter(id=self.account1.id).count(), 0)


class TransactionTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.account1 = Account.objects.create(user=self.user1, balance=Decimal('100.00'))
        self.account2 = Account.objects.create(user=self.user2, balance=Decimal('200.00'))
        self.transaction1 = Transaction.objects.create(
            account=self.account1, to_account=self.account2, amount=Decimal('50.00'), transaction_type='transfer'
        )
        self.transaction2 = Transaction.objects.create(
            account=self.account1, amount=Decimal('30.00'), transaction_type='withdraw'
        )
        self.client = APIClient()

        # Obtain JWT tokens for authentication
        self.refresh_token = RefreshToken.for_user(self.user1)
        self.access_token = self.refresh_token.access_token

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_list_transactions(self):
        response = self.client.get(reverse('transaction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_transactions_by_account_id(self):
        response = self.client.get(reverse('transaction-list'), {'account_id': self.account1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_transactions_by_to_account_id(self):
        response = self.client.get(reverse('transaction-list'), {'to_account_id': self.account2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['to_account'], self.account2.id)

    def test_list_transactions_by_transaction_type(self):
        response = self.client.get(reverse('transaction-list'), {'transaction_type': 'withdraw'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['transaction_type'], 'withdraw')

    def test_list_transactions_by_multiple_filters(self):
        response = self.client.get(reverse('transaction-list'), {
            'account_id': self.account1.id,
            'transaction_type': 'transfer'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['transaction_type'], 'transfer')
        self.assertEqual(response.data[0]['account'], self.account1.id)


class AccountTransactionTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.account1 = Account.objects.create(user=self.user1, balance=Decimal('100.00'))
        self.account2 = Account.objects.create(user=self.user2, balance=Decimal('200.00'))
        self.client = APIClient()

        # Obtain JWT tokens for authentication
        self.refresh_token = RefreshToken.for_user(self.user1)
        self.access_token = self.refresh_token.access_token

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_deposit(self):
        data = {
            'amount': '50.00'
        }
        response = self.client.post(reverse('custom_account-deposit', kwargs={'pk': self.account1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('150.00'))
        self.assertEqual(Transaction.objects.filter(account=self.account1, transaction_type='deposit').count(), 1)

    def test_withdraw(self):
        data = {
            'amount': '50.00'
        }
        response = self.client.post(reverse('custom_account-withdraw', kwargs={'pk': self.account1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('50.00'))
        self.assertEqual(Transaction.objects.filter(account=self.account1, transaction_type='withdraw').count(), 1)

    def test_withdraw_insufficient_funds(self):
        data = {
            'amount': '150.00'
        }
        response = self.client.post(reverse('custom_account-withdraw', kwargs={'pk': self.account1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('100.00'))
        self.assertEqual(Transaction.objects.filter(account=self.account1, transaction_type='withdraw').count(), 0)

    def test_transfer(self):
        data = {
            'to_account_id': self.account2.id,
            'amount': '50.00'
        }
        response = self.client.post(reverse('custom_account-transfer', kwargs={'pk': self.account1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('50.00'))
        self.assertEqual(self.account2.balance, Decimal('250.00'))
        self.assertEqual(Transaction.objects.filter(account=self.account1, to_account=self.account2, transaction_type='transfer').count(), 1)

    def test_transfer_insufficient_funds(self):
        data = {
            'to_account_id': self.account2.id,
            'amount': '150.00'
        }
        response = self.client.post(reverse('custom_account-transfer', kwargs={'pk': self.account1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('100.00'))
        self.assertEqual(self.account2.balance, Decimal('200.00'))
        self.assertEqual(Transaction.objects.filter(account=self.account1, to_account=self.account2, transaction_type='transfer').count(), 0)

    def test_transfer_same_account(self):
        data = {
            'to_account_id': self.account1.id,
            'amount': '50.00'
        }
        response = self.client.post(reverse('custom_account-transfer', kwargs={'pk': self.account1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, Decimal('100.00'))
        self.assertEqual(Transaction.objects.filter(account=self.account1, transaction_type='transfer').count(), 0)