from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from clinic_app.models import Clinic, Category


class ClinicListView(ListView):
    model = Clinic
    template_name = 'clinic_app/clinics.html'
    context_object_name = 'clinics'
    paginate_by = 9  # Уменьшил для лучшего отображения

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related('services')

        # Фильтрация по категории
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Только активные клиники
        queryset = queryset.filter(is_active=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)

        return context


class ClinicDetailView(DetailView):
    model = Clinic
    template_name = 'clinic_app/clinic.html'
    context_object_name = 'clinic'

    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related(
            'clinic_schedules__weekday',
            'services',
            'reviews__user'
        )