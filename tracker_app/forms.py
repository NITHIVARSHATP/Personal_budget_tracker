from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FinancialGoal,Transaction,Profile
from django.contrib.auth.forms import PasswordChangeForm

class TransactionForm(forms.ModelForm):
    CATEGORY_CHOICES = [
    ('Salary', 'Salary'),
    ('Bonus', 'Bonus'),
    ('Freelance', 'Freelance'),
    ('Interest Income', 'Interest Income'),
    ('Investment Returns', 'Investment Returns'),
    ('Rental Income', 'Rental Income'),
    ('Refund', 'Refund'),
    ('Gift Received', 'Gift Received'),

    ('Food', 'Food'),
    ('Groceries', 'Groceries'),
    ('Dining Out', 'Dining Out'),
    ('Snacks', 'Snacks'),
    ('Rent', 'Rent'),
    ('Mortgage', 'Mortgage'),
    ('Utilities', 'Utilities'),
    ('Electricity', 'Electricity'),
    ('Water', 'Water'),
    ('Internet', 'Internet'),
    ('Phone', 'Phone'),

    ('Transportation', 'Transportation'),
    ('Fuel', 'Fuel'),
    ('Public Transport', 'Public Transport'),
    ('Taxi / Ride-share', 'Taxi / Ride-share'),
    ('Vehicle Maintenance', 'Vehicle Maintenance'),

    ('Healthcare', 'Healthcare'),
    ('Doctor Visit', 'Doctor Visit'),
    ('Medicines', 'Medicines'),
    ('Insurance Premium', 'Insurance Premium'),

    ('Education', 'Education'),
    ('Tuition', 'Tuition'),
    ('Books & Supplies', 'Books & Supplies'),
    ('Online Courses', 'Online Courses'),

    ('Entertainment', 'Entertainment'),
    ('Movies', 'Movies'),
    ('Streaming Services', 'Streaming Services'),
    ('Events & Concerts', 'Events & Concerts'),
    
    ('Personal Care', 'Personal Care'),
    ('Salon & Spa', 'Salon & Spa'),
    ('Clothing', 'Clothing'),
    ('Accessories', 'Accessories'),

    ('Travel', 'Travel'),
    ('Lodging', 'Lodging'),
    ('Flights', 'Flights'),
    ('Vacation Packages', 'Vacation Packages'),

    ('Savings', 'Savings'),
    ('Investments', 'Investments'),
    ('Emergency Fund', 'Emergency Fund'),

    ('Charity', 'Charity'),
    ('Gifts', 'Gifts'),
    ('Donations', 'Donations'),

    ('Business Expense', 'Business Expense'),
    ('Subscription', 'Subscription'),
    ('Software', 'Software'),

    ('Other', 'Other'),
]


    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'transaction_type', 'description', 'date']
        
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]



class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['category', 'amount', 'month']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'month'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})