import random
import logging
from celery import shared_task
from django.core.cache import cache
from users_app.models import SMSVerification
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


User = get_user_model()


logger = logging.getLogger(__name__)


@shared_task
def send_sms_code(email, code):
    try:
        send_mail(
            f'Код подтверждения для {email}',
            f'Ваш код: {code}',
            'imaralievasadbek@yandex.ru',
            [email]
        )
        logger.info({'message': f'Код подтверждения отправлен на {email}.'})
    except Exception as e:
        logger.error({'error': f'Ошибка при отправке кода на {email}: {str(e)}'})
        raise e


# Задача для сохранения кода в базе данных
@shared_task
def save_code_in_db(email, code=None):
    if code is None:
        logger.error(f"Код для {email} не может быть пустым.")
        return
    try:
        sms_verification, created = SMSVerification.objects.get_or_create(
            email=email,
            code=code
        )
        if created:
            logger.info(f"Создана запись в БД для {email}")
        else:
            logger.info(f"Запись для {email} обновлена с новым кодом")
    except Exception as e:
        logger.error(f"Ошибка сохранения кода в базе данных для {email}: {e}")
        raise e


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









