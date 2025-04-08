from django.core.cache import cache

EMAIL_CODE_TTL = 300  # 5 минут
EMAIL_CACHE_PREFIX = 'sms_code_'  # Изменено для соответствия tasks.py

def validate_code(email, code):
    key = f'{EMAIL_CACHE_PREFIX}{email}'
    cached_code = cache.get(key)
    if cached_code and str(cached_code) == str(code):
        cache.delete(key)
        return True
    return False