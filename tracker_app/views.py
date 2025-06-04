from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from .models import Transaction  # or your model for transactions
from .forms import FinancialGoalForm
from .models import FinancialGoal

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



@login_required(login_url='login')
def set_goal_view(request):
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Goal saved successfully.")
            return redirect('set_goal')
    else:
        form = FinancialGoalForm()
    
    user_goals = FinancialGoal.objects.filter(user=request.user).order_by('-month')
    return render(request, 'set_goal.html', {'form': form, 'goals': user_goals})


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
    # Pass the current user to the template to show info
    return render(request, 'profile.html', {'user': request.user})

@login_required(login_url='login')
def settings_view(request):
    # For now just render the settings page; can extend later for changing settings
    return render(request, 'settings.html', {'user': request.user})

@login_required(login_url='login')
def reports_view(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'reports.html', {'transactions': transactions})
