from datetime import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from clinic_app.models import Clinic, Service, WeekDay

User = get_user_model()

'''
Вот так вот получаем(для заметки написал)
doctor = Doctor.objects.get(id=1)
schedule_doctor = doctor.schedules.all()
'''
class ScheduleDoctor(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='schedules')
    weekday = models.ForeignKey(WeekDay, on_delete=models.CASCADE, verbose_name='День недели')
    open_time = models.TimeField(verbose_name='Выход на работу(во сколько?)')
    close_time = models.TimeField(verbose_name='Уход с работы(во сколько?)')
    is_working = models.BooleanField(default=True, verbose_name='Рабочий день?')

    class Meta:
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'
        unique_together = ('clinic', 'weekday')
        ordering = ['weekday__order']

    def __str__(self):
        return f"{self.clinic.name} - {self.weekday.name}"


# Специализация
class Specialization(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название специализаций')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL-имя')
    description = models.TextField(verbose_name='Описание специализаций')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')



class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name='Пользователь'
    )
    clinics = models.ManyToManyField(
        Clinic,
        related_name='doctors',
        verbose_name='Клиники'
    )
    first_name = models.CharField(max_length=25, verbose_name='Имя')
    last_name = models.CharField(max_length=25, verbose_name='Фамилия')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, verbose_name='Специализация')
    contact_phone = models.CharField(max_length=20, verbose_name='Контактный телефон', null=True, blank=True)
    bio = models.TextField(max_length=1000, verbose_name='Биография')
    photo = models.ImageField(upload_to='doctors/', verbose_name='Фото', null=True, blank=True)
    serviced_patients_number = models.PositiveSmallIntegerField(verbose_name='Количество обслуженных пациентов')
    experience = models.PositiveSmallIntegerField(verbose_name='Опыт работы (лет)')
    education = models.TextField(verbose_name='Образование')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Рейтинг'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return f"{self.user.username} ({self.specialization})"


# Запись на прием
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Пациент'
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Клиника'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='Услуга'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='Врач'
    )
    date = models.DateField(verbose_name='Дата приема')
    time = models.TimeField(verbose_name='Время приема')
    end_time = models.TimeField(verbose_name='Время окончания', blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус записи'
    )
    notes = models.TextField(max_length=500, blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Запись на прием'
        verbose_name_plural = 'Записи на прием'
        ordering = ['date', 'time']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.end_time and self.service:
            from datetime import timedelta
            self.end_time = (datetime.combine(self.date, self.time) +
                             timedelta(minutes=self.service.duration)).time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Запись #{self.id} - {self.user.username}"



class ReviewDoctor(models.Model):
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
        related_name='reviews',
        verbose_name='Пользователь'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Доктор'
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


