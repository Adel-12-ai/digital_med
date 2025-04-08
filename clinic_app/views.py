from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Clinics


def clinic_view(request):
    clinics = Clinics.objects.all()
    return render(request, 'clinic_app/clinics.html', context={'clinics':clinics})


def clinic_detail_view(request, clinic_id):
    try:
        clinic = Clinics.objects.get(pk = clinic_id)
    except Clinics.DoesNotExist:
        raise Http404('Клиники не существует')
    return render(request, 'clinic_view.html', context={'clinic' : clinic})



