from django.shortcuts import render


def clinic_view(request):
    return render(request, 'clinic_app/index.html')

