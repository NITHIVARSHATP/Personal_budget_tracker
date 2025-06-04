from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # e.g., 'income' or 'expense'
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.category} - {self.amount}"

class FinancialGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)  # e.g., "Food", "Savings", "Rent"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()  # store month as date (we can use just year-month for filtering)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.month.strftime('%Y-%m')} - ₹{self.amount}"
