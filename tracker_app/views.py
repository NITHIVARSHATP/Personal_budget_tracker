from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='login') 
def home_view(request):
    return render(request, 'home.html')

def add_transaction_view(request):
    return render(request, 'add_transaction.html')

def transactions_list_view(request):
    return render(request, 'transactions_list.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')  # Replace with your login URL name
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})
