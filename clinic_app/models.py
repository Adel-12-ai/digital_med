from datetime import date
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


User = get_user_model()


class WeekDay(models.Model):
    name = models.CharField(max_length=15, verbose_name='День недели')
    short_name = models.CharField(max_length=2, verbose_name='Сокращение')
    order = models.PositiveSmallIntegerField(unique=True, verbose_name='Порядок')

    class Meta:
        verbose_name = 'День недели'
        verbose_name_plural = 'Дни недели'
        ordering = ['order']

    def __str__(self):
        return self.name


class ScheduleClinic(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE, related_name='clinic_schedules')
    weekday = models.ForeignKey(WeekDay, on_delete=models.CASCADE, verbose_name='День недели')
    open_time = models.TimeField(verbose_name='Время открытия')
    close_time = models.TimeField(verbose_name='Время закрытия')
    is_working = models.BooleanField(default=True, verbose_name='Рабочий день?')

    class Meta:
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'
        unique_together = ('clinic', 'weekday')
        ordering = ['weekday__order']

    def __str__(self):
        return f"{self.clinic.name} - {self.weekday.name}"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL-имя')
    description = models.TextField(max_length=500, verbose_name='Описание категории')
    image = models.ImageField(upload_to='categories/', default=None, verbose_name='Фото категории')
    is_active = models.BooleanField(default=True, verbose_name='Активна?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Clinic(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL-имя')
    description = models.TextField(max_length=1000, verbose_name='Описание')
    short_description = models.CharField(max_length=200, verbose_name='Краткое описание')
    location = models.TextField(verbose_name='Адрес')
    contact_phone = models.CharField(max_length=20, verbose_name='Контактный телефон')
    contact_email = models.EmailField(verbose_name='Контактный email')
    image = models.ImageField(upload_to='clinics/', default=None, verbose_name='Фото клиники')
    logo = models.ImageField(upload_to='clinics/logos/', default=None, verbose_name='Логотип')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Рейтинг'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='clinics',
        verbose_name='Категория'
    )
    is_verified = models.BooleanField(default=False, verbose_name='Проверенная клиника?')
    is_active = models.BooleanField(default=True, verbose_name='Активна?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Клиника'
        verbose_name_plural = 'Клиники'
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-rating', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    slug = models.SlugField(max_length=100, verbose_name='URL-имя')
    description = models.TextField(max_length=500, verbose_name='Описание услуги')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        validators=[MinValueValidator(0)]
    )
    duration = models.PositiveSmallIntegerField(
        verbose_name='Длительность (мин)',
        help_text='Продолжительность услуги в минутах'
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Клиника'
    )
    doctors = models.ManyToManyField(
        'doctors_app.Doctor',
        related_name='services',
        verbose_name='Врачи',
        blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        unique_together = ('clinic', 'slug')
        ordering = ['price']

        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.clinic.name})"


class ReviewClinic(models.Model):
    RATING_CHOICES = [
        (1, '1 - Плохо'),
        (2, '2 - Удовлетворительно'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    MODERATION_STATUS = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clinic_reviews',
        verbose_name='Пользователь'
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Клиника'
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name='Оценка'
    )
    text = models.TextField(max_length=1000, verbose_name='Текст отзыва')
    moderation_status = models.CharField(
        max_length=10,
        choices=MODERATION_STATUS,
        default='pending',
        verbose_name='Статус модерации'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('user', 'clinic')
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return f"Отзыв от {self.user.email} для {self.clinic.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновляем рейтинг клиники при сохранении отзыва
        if self.moderation_status == 'approved':
            self.clinic.update_rating()




