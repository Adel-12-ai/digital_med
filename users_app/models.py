from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None):
        if not email:
            raise ValueError('Необходимо указать email!')

        user = self.model(email=email)
        user.set_unusable_password()  # Пароль не обязателен, так как логика через SMS
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None):
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='email')
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.email)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]


class SMSVerification(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=4, verbose_name='Код')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'email Пользователя: {self.email} Код: {self.code}'

    def is_code_valid(self):
        return (
            timezone.now() < self.created_at + timedelta(minutes=3) and not self.is_used
        )

    class Meta:
        indexes = [
            models.Index(fields=['email', 'code', 'created_at']),
        ]






