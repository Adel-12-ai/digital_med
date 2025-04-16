from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy

from django.http import JsonResponse

from doctors_app.models import Doctor
from .models import SMSVerification, Appointment
from .forms import SignUserForm, VerificationUserForm, AppointmentForm
from django.contrib.auth import get_user_model, login, logout

from .services.code_limited_service import(
    is_code_rate_limit, set_code_rate_limited, delete_code_in_cache
)
from .services.validate_code_service import validate_code
from .tasks import generate_and_save_and_send_code, send_appointment_task
import logging


logger = logging.getLogger(__name__)

User = get_user_model()


def sign_user_view(request):
    if request.method == 'POST':
        sign_form = SignUserForm(request.POST)
        if sign_form.is_valid():
            email = sign_form.cleaned_data['email']

            # Проверяем, не существует ли уже активный пользователь
            if User.objects.filter(email=email, is_active=True).exists():
                messages.error(request, 'Пользователь с этим email уже зарегистрирован')
                return redirect('users_app:sign_user')

            if is_code_rate_limit(email):
                messages.error(request, 'Попробуйте позже — лимит на отправку кода.')
                return redirect('users_app:sign_user')

            # Отправляем код
            code_task = generate_and_save_and_send_code.delay(email)
            try:
                code = code_task.get(timeout=5)  # Ждем результат задачи
            except:
                code = None

            if not code:
                messages.error(request, 'Не удалось отправить код. Попробуйте позже.')
                return redirect('users_app:sign_user')

            # Сохраняем email в сессии и в куках на случай истечения сессии
            request.session['verification_email'] = email
            response = redirect('users_app:verify_email')
            response.set_cookie('verification_email', email, max_age=300)  # 5 минут
            set_code_rate_limited(email)

            return response

    else:
        sign_form = SignUserForm()

    return render(request, 'users_app/sign_user.html', {'form': sign_form})


def verify_user_view(request):
    # Получаем email из сессии или куков
    email = request.session.get('verification_email') or request.COOKIES.get('verification_email')
    if not email:
        messages.error(request, 'Сессия истекла. Пожалуйста, начните процесс заново.')
        return redirect('users_app:sign_user')

    if request.method == 'POST':
        verify_form = VerificationUserForm(request.POST)
        if verify_form.is_valid():
            form_email = verify_form.cleaned_data['email']
            code = verify_form.cleaned_data['code']

            # Дополнительная проверка email
            if form_email != email:
                messages.error(request, 'Несоответствие email. Начните процесс заново.')
                return redirect('users_app:sign_user')

            if validate_code(email, code):
                try:
                    verification = SMSVerification.objects.get(
                        email=email,
                        code=code,
                        is_used=False
                    )
                    verification.is_used = True
                    verification.save()

                    # Создаем или активируем пользователя
                    user, created = User.objects.get_or_create(email=email)
                    if not created and user.is_active:
                        messages.error(request, 'Этот email уже зарегистрирован')
                        return redirect('users_app:sign_user')

                    user.is_active = True
                    user.save()
                    login(request, user)

                    # Очищаем сессию и куки
                    if 'verification_email' in request.session:
                        del request.session['verification_email']
                    delete_code_in_cache(email)

                    response = redirect('clinic_app:clinics')
                    response.delete_cookie('verification_email')
                    messages.success(request, 'Ваш email успешно подтвержден!')
                    return response

                except SMSVerification.DoesNotExist:
                    messages.error(request, 'Неверный код подтверждения')
            else:
                messages.error(request, 'Неверный код подтверждения')

    else:
        verify_form = VerificationUserForm(initial={'email': email})

    return render(request, 'users_app/verify_email.html', {
        'form': verify_form,
        'email': email
    })


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли с аккаунта!')
    return redirect('clinic_app:clinics')


# Пошли Апоинтменты
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'users_app/send_appointment.html'
    success_url = reverse_lazy('users_app:appointments')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Формируем детали записи
        appointment_details = (
            f"Клиника: {form.instance.clinic.name}\n"
            f"Врач: {form.instance.doctor.first_name} {form.instance.doctor.last_name}\n"
            f"Дата: {form.instance.date}\n"
            f"Время: {form.instance.time}\n"
            f"Примечания: {form.instance.notes or 'Нет примечаний'}"
        )

        # Отправляем уведомление
        send_appointment_task.delay(
            user_email=self.request.user.email,
            message=appointment_details
        )

        messages.success(self.request, 'Запись успешно создана! Проверьте вашу почту.')
        return response


class AppointmentListView(ListView):
    model = Appointment
    template_name = 'users_app/appointments.html'
    context_object_name = 'appointments'


class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = 'users_app/appointment.html'
    context_object_name = 'appointment'


class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'users_app/appointment_update.html'
    success_url = reverse_lazy('users_app:appointments')  # Редирект после успеха


class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = 'users_app/appointment_delete.html'
    success_url = reverse_lazy('users_app:appointments')  # Редирект после успеха


def get_doctors(request):
    clinic_id = request.GET.get('clinic_id')
    doctors = Doctor.objects.filter(clinics__id=clinic_id)
    options = '<option value="">Выберите врача</option>'
    for doctor in doctors:
        options += f'<option value="{doctor.id}">{doctor.first_name} {doctor.last_name}</option>'
    return JsonResponse(options, safe=False)

