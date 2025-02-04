from django.db import models
from accounts.models import Accounts

class Wallet(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE, related_name='user_wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet - ₹{self.balance}"

    @classmethod
    def get_or_create(cls, user):
        wallet, created = cls.objects.get_or_create(user=user)
        return wallet

    def add_money(self, amount):
        self.balance += amount
        self.save()
        WalletHistory.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='CREDIT',
            notes=f"Added ₹{amount} to wallet"
        )
        return self.balance

    def deduct_money(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            WalletHistory.objects.create(
                wallet=self,
                amount=amount,
                transaction_type='DEBIT',
                notes=f"Deducted ₹{amount} from wallet"
            )
            return True
        return False

class WalletHistory(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
        ('REFUND', 'Refund'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    notes = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
