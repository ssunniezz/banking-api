from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    pass  # Extend as needed

    # Override groups and user_permissions
    groups = None
    user_permissions = None


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=[('THB', 'Thai Baht'), ('USD', 'US Dollar')], default='THB')
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_transfers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=[('THB', 'Thai Baht'), ('USD', 'US Dollar')], default='THB')
    real_amount = models.DecimalField(max_digits=10, decimal_places=2)
    real_currency = models.CharField(max_length=3, choices=[('THB', 'Thai Baht'), ('USD', 'US Dollar')], default='THB')
    transaction_type = models.CharField(max_length=10, choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw'), ('transfer', 'Transfer')])
    created_at = models.DateTimeField(auto_now_add=True)

