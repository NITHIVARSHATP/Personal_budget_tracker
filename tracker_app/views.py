from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Render a template called home.html
