from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from clinic_app.models import Clinic, Category, Service


class ClinicListView(ListView):
    model = Clinic
    template_name = 'clinic_app/clinics.html'
    context_object_name = 'clinics'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related('services')

        # Фильтрация по категории из GET-параметра
        self.category_slug = self.request.GET.get('category')
        if self.category_slug:
            queryset = queryset.filter(category__slug=self.category_slug)

        # Только активные клиники
        queryset = queryset.filter(is_active=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Все активные категории для dropdown меню
        context['categories'] = Category.objects.filter(is_active=True)

        # Текущая выбранная категория
        if hasattr(self, 'category_slug') and self.category_slug:
            context['current_category'] = get_object_or_404(Category, slug=self.category_slug)
            context['hide_header'] = True  # Флаг для скрытия шапки

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


class CategoryListView(ListView):
    model = Category
    template_name = 'clinic_app/categories.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class ServicesListView(ListView):
    model = Service
    template_name = 'clinic_app/services.html'
    context_object_name = 'services'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset().select_related('clinic', 'clinic__category')

        # Фильтрация по активным услугам
        queryset = queryset.filter(is_active=True)

        # Фильтрация по клинике (если передан clinic_id)
        clinic_id = self.request.GET.get('clinic_id')
        if clinic_id:
            queryset = queryset.filter(clinic_id=clinic_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic_id'] = self.request.GET.get('clinic_id')
        return context


class ServicesDetailView(DetailView):
    model = Service
    template_name = 'clinic_app/service.html'
    context_object_name = 'service'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'clinic', 'clinic__category'
        ).prefetch_related(
            'doctors', 'doctors__specialization'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object
        context['related_services'] = Service.objects.filter(
            clinic=service.clinic,
            is_active=True
        ).exclude(id=service.id)[:4]
        return context


# contact us
def contact_us(request):
    return render(request, 'clinic_app/contact.html')


# contact us
from django.views.generic import TemplateView


class AboutUsView(TemplateView):
    template_name = 'clinic_app/about_us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Можно добавить дополнительные данные в контекст
        context['page_title'] = 'О нашей клинике'
        return context
