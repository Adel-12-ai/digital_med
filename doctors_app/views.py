from django.shortcuts import render, get_object_or_404

from django.views.generic import(
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from clinic_app.models import Clinic
from users_app.models import Appointment
from .models import (
    Doctor, ReviewDoctor, ScheduleDoctor, Specialization
)

class DoctorListView(ListView):
    model = Doctor
    context_object_name = 'doctors'
    template_name = 'doctors_app/doctors.html'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['specialization'] = Specialization.objects.filter(is_active=True)

        # Текущая выбранная специализация
        if hasattr(self, 'specialization_slug') and self.specialization_slug:
            context['current_specialization'] = get_object_or_404(Specialization, slug=self.specialization_slug)
            context['hide_header'] = True  # Флаг для скрытия шапки

        return context


class DoctorDetailView(DetailView):
    model = Doctor
    context_object_name = 'doctor'
    template_name = 'doctors_app/doctor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем все клиники, связанные с этим доктором
        context['clinics'] = self.object.clinics.all()

        return context

    def get_queryset(self):
        return super().get_queryset().select_related('specialization').prefetch_related(
            'doctor_schedules__weekday',
            'reviews__user',
        )


class AppointmentsListView(ListView):
    model = Appointment
    context_object_name = 'appointments'
    template_name = 'doctors_app/appointments.html'



class AppointmentsDetailView(DetailView):
    model = Appointment
    context_object_name = 'appointment'
    template_name = 'doctors_app/appointment.html'



