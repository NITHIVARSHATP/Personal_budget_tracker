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
from django.utils.timezone import now
from .models import Goal
from .forms import GoalForm

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
    last_goal = Goal.objects.filter(user=request.user).order_by('-created_at').first()

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = GoalForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            income_goal = form.cleaned_data['income_goal']
            expense_goal = form.cleaned_data['expense_goal']

            goal, created = Goal.objects.update_or_create(
                user=request.user,
                month=month,
                defaults={'income_goal': income_goal, 'expense_goal': expense_goal}
            )

            progress = (goal.expense_goal / goal.income_goal) * 100 if goal.income_goal > 0 else 0

            return JsonResponse({
                "income_goal": float(goal.income_goal),
                "expense_goal": float(goal.expense_goal),
                "month": goal.month,
                "created_at": goal.created_at.strftime('%B %d, %Y'),
                "expense_progress": round(progress, 2),
                "goal_alert": "You’ve exceeded your budget!" if progress >= 100 else "Great job staying within your budget!"
            })
        else:
            return JsonResponse({"error": "Invalid form"}, status=400)

    return render(request, "set_goal.html", {"last_goal": last_goal})

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
    # 1. Get selected month or default to current
    month_label = request.GET.get("month", now().strftime("%B %Y"))

    try:
        selected_date = datetime.strptime(month_label, "%B %Y")
    except ValueError:
        selected_date = now()

    selected_month_number = selected_date.month
    selected_year = selected_date.year
    month_label = selected_date.strftime("%B %Y")  # Reformat

    # 2. Get all transactions by the user
    all_transactions = Transaction.objects.filter(user=request.user)

    # 3. Filter transactions by selected month
    transactions = all_transactions.filter(
        date__month=selected_month_number,
        date__year=selected_year
    )

    # 4. Build the month dropdown from all available transactions
    months = sorted(
        set(t.date.strftime("%B %Y") for t in all_transactions),
        reverse=True
    )

    # 5. Totals
    income_total = sum(t.amount for t in transactions if t.transaction_type == 'income')
    expense_total = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = income_total - expense_total

    # 6. Percentages
    expense_percent = round((expense_total / income_total) * 100, 2) if income_total > 0 else 0
    balance_percent = round((balance / income_total) * 100, 2) if income_total > 0 else 0

    # 7. Goal Progress and Alert (Match Goal.month as DATE field)
    goal_alert = None
    expense_progress_percent = None
    try:
        goal_month = selected_date.strftime("%B %Y")  # ➤ "July 2025"
        goal = Goal.objects.filter(user=request.user, month=goal_month).first()

        if goal:
            # Calculate progress toward the monthly goal
            if goal.expense_goal > 0:
                expense_progress_percent = round((expense_total / goal.expense_goal) * 100, 2)
            else:
                expense_progress_percent = 0

            # Set alert message
            if expense_total > goal.expense_goal:
                goal_alert = f"⚠️ You have exceeded your expense goal of ₹{goal.expense_goal:.2f} for {month_label}."
            else:
                remaining = goal.expense_goal - expense_total
                goal_alert = f"✅ You still have ₹{remaining:.2f} left to spend for {month_label}."
    except Exception as e:
        goal_alert = None  # Optional: log error

    # 8. Render context
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
