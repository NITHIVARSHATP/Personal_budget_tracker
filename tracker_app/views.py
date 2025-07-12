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
from .models import Profile 
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import StyledPasswordChangeForm
from django.http import JsonResponse
from decimal import Decimal
from django.utils.dateparse import parse_date
from datetime import datetime
from django.db.models import Sum

def logout_view(request):
    logout(request)
    return redirect('login') 
    
@login_required
def export_report_csv(request):
    selected_month = request.GET.get("month")
    if selected_month:
        try:
            month_dt = datetime.strptime(selected_month, "%B %Y")
            transactions = Transaction.objects.filter(
                user=request.user,
                date__month=month_dt.month,
                date__year=month_dt.year
            ).order_by('-date')
        except ValueError:
            transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    else:
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Type', 'Description'])

    for t in transactions:
        writer.writerow([t.date, t.category, t.amount, t.transaction_type, t.description])

    return response



@login_required
def export_report_pdf(request):
    selected_month = request.GET.get("month")
    if selected_month:
        try:
            month_dt = datetime.strptime(selected_month, "%B %Y")
            transactions = Transaction.objects.filter(
                user=request.user,
                date__month=month_dt.month,
                date__year=month_dt.year
            ).order_by('-date')
        except ValueError:
            transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    else:
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')

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
        income_goal = float(request.POST.get('income_goal'))
        expense_goal = float(request.POST.get('expense_goal'))
        month_input = request.POST.get('month')  # "2025-07"

        try:
            month_dt = datetime.strptime(month_input, "%Y-%m")
            month_str = month_dt.strftime("%B %Y")  # "July 2025"
        except:
            return JsonResponse({'error': 'Invalid month format'}, status=400)

        # Update or create goal
        goal, created = Goal.objects.update_or_create(
            user=request.user,
            month=month_str,
            defaults={
                'income_goal': income_goal,
                'expense_goal': expense_goal
            }
        )

        # Optionally calculate progress/alert like before
        expense_total = Transaction.objects.filter(
            user=request.user,
            date__month=month_dt.month,
            date__year=month_dt.year,
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0

        expense_progress = round((expense_total / Decimal(expense_goal)) * 100, 2) if expense_goal else 0

        alert = (
            f"⚠️ You have exceeded your expense goal of ₹{expense_goal:.2f} for {month_str}."
            if expense_total > expense_goal
            else f"✅ You still have ₹{Decimal(expense_goal) - expense_total:.2f} left to spend for {month_str}."
        )

        return JsonResponse({
            'income_goal': income_goal,
            'expense_goal': expense_goal,
            'month': month_str,
            'created_at': goal.created_at.strftime("%B %d, %Y"),
            'expense_progress': expense_progress,
            'goal_alert': alert
        })

    # GET: Show last goal
    last_goal = Goal.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, 'set_goal.html', {'last_goal': last_goal})

def home_view(request):
    tiles = [
        {"url": "add_transaction", "icon": "plus-circle-fill", "color": "success", "title": "Add Transaction", "desc": "Add income or expense entries."},
        {"url": "transactions_list", "icon": "list-task", "color": "primary", "title": "Transactions", "desc": "View and manage transactions."},
        {"url": "dashboard", "icon": "speedometer2", "color": "warning", "title": "Dashboard", "desc": "Analyze your financial health."},
        {"url": "reports", "icon": "file-earmark-bar-graph", "color": "secondary", "title": "Reports", "desc": "Monthly downloadable reports."},
        {"url": "set_goal", "icon": "bullseye", "color": "info", "title": "Set Goal", "desc": "Plan savings and objectives."},
        {"url": "register", "icon": "person-plus", "color": "dark", "title": "Register", "desc": "Create a new account."},
        {"url": "login", "icon": "box-arrow-in-right", "color": "danger", "title": "Login", "desc": "Access your dashboard."}
    ]
    return render(request, 'home.html', {'tiles': tiles})


# Add Transaction View
@login_required(login_url='login')
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user  
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

    # Filter transactions
    all_transactions = Transaction.objects.filter(user=request.user)
    transactions = all_transactions.filter(
        date__month=selected_month_number,
        date__year=selected_year
    )

    # Unique months for dropdown
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

    # ➕ GOAL ALERT LOGIC
    goal_alert = None
    expense_progress_percent = None
    goal = Goal.objects.filter(user=request.user, month=month_label).first()
    if goal:
        expense_progress_percent = round((expense_total / goal.expense_goal) * 100, 2) if goal.expense_goal else 0
        if expense_total > goal.expense_goal:
            goal_alert = f"⚠️ You have exceeded your expense goal of ₹{goal.expense_goal} for {month_label}."
        else:
            remaining = goal.expense_goal - expense_total
            goal_alert = f"✅ You still have ₹{remaining:.2f} left to spend for {month_label}."

    return render(request, 'dashboard.html', {
        'transactions': transactions,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'months': months,
        'selected_month': month_label,
        'expense_percent': expense_percent,
        'balance_percent': balance_percent,
        'income_percent': 100,
        'goal_alert': goal_alert,
        'expense_progress_percent': expense_progress_percent,
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
    profile, created = Profile.objects.get_or_create(user=user)

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



class CustomPasswordChangeView(PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')  # or use 'settings' if preferred
