from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import SMSVerification
from .forms import SignUserForm, VerificationUserForm
from django.contrib.auth import get_user_model, login, logout

from .services.code_limited_service import(
    is_code_rate_limit, set_code_rate_limited, delete_code_in_cache
)
from .services.validate_code_service import validate_code
from .tasks import generate_and_save_and_send_code
import logging


logger = logging.getLogger(__name__)

User = get_user_model()


def sign_user_view(request):
    if request.method == 'POST':
        sign_form = SignUserForm(request.POST)
        if sign_form.is_valid():
            email = sign_form.cleaned_data['email']

            if is_code_rate_limit(email):
                sign_form.add_error('email', 'Попробуйте позже — лимит на отправку кода.')

            code = generate_and_save_and_send_code.delay(email)

            if not code:
                logger.error(f'Ошибка при отправке SMS(Ошибка тут)')
                sign_form.add_error('code', 'Не удалось отправить код.')
                return redirect('users_app:sign_user')

            # Сохраняем email в сессии для использования на следующем шаге
            request.session['email'] = email
            set_code_rate_limited(email)

            return redirect('users_app:verify_email')

    else:
        sign_form = SignUserForm(request.POST)

    context = {
        'form': sign_form
    }
    return render(request, 'users_app/sign_user.html', context)


def verify_user_view(request):
    email = request.session.get('email')
    if request.method == 'POST':
        verify_form = VerificationUserForm(request.POST)
        if verify_form.is_valid():
            email = verify_form.cleaned_data['email']
            code = verify_form.cleaned_data['code']
            if not email:
                verify_form.add_error('email', 'email обьязателен.')
            if not code:
                verify_form.add_error('code', 'Код обьязателен.')

            if validate_code(email, code):
                verification = SMSVerification.objects.get(
                    email=email,
                    code=code,
                    is_used=False
                )
                verification.is_used = True
                verification.save()

                # Создаем пользователя после подтверждения подлинности email
                user, created = User.objects.get_or_create(
                    email=email
                )
                user.is_active = True
                user.save()
                login(request, user)

                # Удаляет Кэш
                delete_code_in_cache(email)

                messages.success(request, 'Ваш email успешно подтвержден!')
                return redirect('clinic_app:home')  # Redirect to profile completion

            else:
                messages.error(request, 'Неверный код подтверждения')
                return redirect('users_app:verify_email')

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
    return redirect('clinic_app:home')

