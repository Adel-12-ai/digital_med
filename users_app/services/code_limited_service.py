from django.core.cache import cache


EMAIL_CODE_TTL = 300  # 5 минут
LIMIT_CACHE_PREFIX = 'time_limit_'
EMAIL_CACHE_PREFIX = 'sms_code_'  # Изменено для соответствия tasks.py


# Возвращаем из кэша что-нибудь, что не Nоne
def is_code_rate_limit(email):
    return cache.get(f'{LIMIT_CACHE_PREFIX}{email}') is not None


# Установка лимита
def set_code_rate_limited(email):
    return cache.set(f'{LIMIT_CACHE_PREFIX}{email}', True, timeout=EMAIL_CODE_TTL)


# Удалитель кэша
def delete_code_in_cache(email):
    key = f'{EMAIL_CACHE_PREFIX}{email}'
    return cache.delete(key)



