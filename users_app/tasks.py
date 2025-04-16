import random
import logging
from celery import shared_task
from django.core.cache import cache
from users_app.models import SMSVerification
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from datetime import datetime

from dotenv import load_dotenv
import os

User = get_user_model()

# from .env
load_dotenv()


logger = logging.getLogger(__name__)


@shared_task
def send_sms_code(email, code):
    cache_key = f"sms_limit_{email}"

    if cache.get(cache_key):
        logger.warning(f"Превышено количество запросов для {email}.")
        return

    try:
        send_mail(
            f'Код подтверждения для {email}',
            f'Ваш код: {code}',
            os.getenv('FROM_EMAIL'),
            [email]
        )
        cache.set(cache_key, True, timeout=60)  # Ограничение: 1 запрос в минуту
        logger.info(f"Код подтверждения отправлен на {email}.")
    except Exception as e:
        logger.error(f"Ошибка при отправке кода: {str(e)}")
        raise e


# Задача для сохранения кода в базе данных
@shared_task
def save_code_in_db(email, code=None):
    if code is None:
        logger.error(f"Код для {email} не может быть пустым.")
        return
    try:
        user = User.objects.get_or_create(email=email)
        if not user:
            logger.error(f"Пользователь с email {email} не найден.")
            return
        sms_verification, created = SMSVerification.objects.update_or_create(
            email=email,
            defaults={'code': code, 'is_used': False, 'created_at': timezone.now()}
        )
        logger.info(f"Код сохранен в базе для {email}.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении кода для {email}: {str(e)}")



@shared_task
def generate_and_save_and_send_code(email):
    try:
        code = f"{random.randint(1000, 9999)}"

        send_sms_code.delay(email, code)
        cache.set(f'sms_code_{email}', code, timeout=300)
        save_code_in_db.delay(email, code)
        logger.info(f"Код {code} сгенерирован и отправлен для {email}.")
        return code  # Возвращаем сгенерированный код
    except Exception as e:
        logger.error(f"Ошибка генерации кода для {email}: {e}")
        return None  # Возвращаем None в случае ошибки


# Для очистки устаревших верификаций
@shared_task
def cleanup_expired_sms_verifications():
    expired_sms = SMSVerification.objects.filter(
        created_at__lt=timezone.now() < timedelta(minutes=3)
    )
    return expired_sms.delete()


@shared_task
def send_appointment_task(user_email, message):
    # Письмо клинике (отправляем с официального адреса)
    send_mail(
        subject=f'Новая запись на прием от {user_email}',
        message=f"Клиент {user_email} оставил запрос:\n\n{message}",
        from_email=os.getenv('FROM_EMAIL'),  # Официальный адрес системы
        recipient_list=['asadullahgits@gmail.com'],  # Адрес клиники
        fail_silently=False
    )

    # Письмо подтверждения клиенту
    send_mail(
        subject='Ваш запрос успешно принят!',
        message='Ваша запись на прием принята. Ожидайте подтверждения от клиники.',
        from_email=os.getenv('FROM_EMAIL'),  # Официальный адрес системы
        recipient_list=[user_email],  # Адрес клиента
        fail_silently=False
    )

    logger.info('Уведомления о записи отправлены')







