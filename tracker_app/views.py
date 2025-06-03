from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm



# Home View (Dashboard Preview Page)
@login_required(login_url='login')
def home_view(request):
    return render(request, 'home.html')

# Add Transaction View
@login_required(login_url='login')
def add_transaction_view(request):
    return render(request, 'add_transaction.html')

# Transactions List View
@login_required(login_url='login')
def transactions_list_view(request):
    return render(request, 'transactions_list.html')

# Dashboard View
@login_required(login_url='login')
def dashboard_view(request):
    # You can later fetch actual transaction data here and pass it to the template
    return render(request, 'dashboard.html')

# Register View
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'profile.html')

@login_required(login_url='login')
def settings_view(request):
    return render(request, 'settings.html')


@login_required(login_url='login')
def profile_view(request):
    # Pass the current user to the template to show info
    return render(request, 'profile.html', {'user': request.user})

@login_required(login_url='login')
def settings_view(request):
    # For now just render the settings page; can extend later for changing settings
    return render(request, 'settings.html', {'user': request.user})