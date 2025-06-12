from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm,FinancialGoalForm,TransactionForm,UserForm, ProfileForm
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from .models import Transaction,Goal, FinancialGoal
from django.contrib.auth import logout
from datetime import datetime

def logout_view(request):
    logout(request)
    return redirect('login') 
    
def export_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Type', 'Description'])  # headers
    transactions = Transaction.objects.all().order_by('-date')
    for t in transactions:
        writer.writerow([t.date, t.category, t.amount, t.transaction_type, t.description])
    return response


def export_report_pdf(request):
    transactions = Transaction.objects.all().order_by('-date')
    html = render_to_string('report_pdf_template.html', {'transactions': transactions})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions_report.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors while generating PDF <pre>' + html + '</pre>')
    
    return response


@login_required
def set_goals_view(request):
    if request.method == "POST":
            income_goal = request.POST.get('income_goal')
            expense_goal = request.POST.get('expense_goal')
            month = request.POST.get('month')

            Goal.objects.create(
                user=request.user,
                income_goal=income_goal,
                expense_goal=expense_goal,
                month=month,
            )
            return redirect('set_goal')  # reload the same page to show updated info

        # For GET request: get last goal set by this user (if any)
    last_goal = Goal.objects.filter(user=request.user).order_by('-created_at').first()

    return render(request, 'set_goal.html', {'last_goal': last_goal})

# Home View (Dashboard Preview Page)
@login_required(login_url='login')
def home_view(request):
    return render(request, 'home.html')

# Add Transaction View
@login_required(login_url='login')
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user  # 🔥 Assign logged-in user
            transaction.save()
            return redirect('transactions_list')
    else:
        form = TransactionForm()
    return render(request, 'add_transaction.html', {'form': form})


# Transactions List View
@login_required(login_url='login')
def transactions_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions_list.html', {'transactions': transactions})

@login_required
def dashboard_view(request):
    month_label = request.GET.get("month", datetime.now().strftime("%B %Y"))

    try:
        selected_month_number = datetime.strptime(month_label, "%B %Y").month
        selected_year = datetime.strptime(month_label, "%B %Y").year
    except ValueError:
        selected_month_number = datetime.now().month
        selected_year = datetime.now().year
        month_label = datetime.now().strftime("%B %Y")

    # First get all user transactions
    all_transactions = Transaction.objects.filter(user=request.user)

    # Filter by selected month and year
    transactions = all_transactions.filter(
        date__month=selected_month_number,
        date__year=selected_year
    )

    # Generate unique "Month Year" dropdown list
    months = sorted(set(t.date.strftime("%B %Y") for t in all_transactions), reverse=True)

    # Totals
    income_total = sum(t.amount for t in transactions if t.transaction_type == 'income')
    expense_total = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = income_total - expense_total

    # Percentages
    if income_total > 0:
        expense_percent = round((expense_total / income_total) * 100, 2)
        balance_percent = round((balance / income_total) * 100, 2)
    else:
        expense_percent = 0
        balance_percent = 0

    return render(request, 'dashboard.html', {
        'transactions': transactions,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'months': months,
        'selected_month': month_label,
        'expense_percent': expense_percent,
        'balance_percent': balance_percent,
        'income_percent': 100  
    })


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
    # Pass the current user to the template to show info
    return render(request, 'profile.html', {'user': request.user})

@login_required(login_url='login')
def settings_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('settings')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required(login_url='login')
def reports_view(request):
    month_label = request.GET.get("month", datetime.now().strftime("%B %Y"))

    try:
        selected_month = datetime.strptime(month_label, "%B %Y").month
        selected_year = datetime.strptime(month_label, "%B %Y").year
    except ValueError:
        selected_month = datetime.now().month
        selected_year = datetime.now().year
        month_label = datetime.now().strftime("%B %Y")

    all_transactions = Transaction.objects.filter(user=request.user)
    transactions = all_transactions.filter(date__month=selected_month, date__year=selected_year)
    
    # Month dropdown options
    months = sorted(set(t.date.strftime("%B %Y") for t in all_transactions), reverse=True)

    return render(request, "reports.html", {
        "transactions": transactions,
        "months": months,
        "selected_month": month_label,
    })

@login_required
def delete_transaction(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)
    transaction.delete()
    return redirect('transactions_list')