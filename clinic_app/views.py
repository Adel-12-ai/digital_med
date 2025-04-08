from django.shortcuts import render


def home_view(request):
    return render(request, 'clinic_app/index.html')

