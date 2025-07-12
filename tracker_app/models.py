from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"


class FinancialGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)  # e.g., "Food", "Savings", "Rent"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()  # store month as date (we can use just year-month for filtering)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.month.strftime('%Y-%m')} - ₹{self.amount}"



class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)  # e.g., "July 2025"
    income_goal = models.DecimalField(max_digits=10, decimal_places=2)
    expense_goal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'month')  # Enforce one goal per user per month

    def __str__(self):
        return f"{self.user.username} - {self.month}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return ''
