from django.db import models
from django.utils.version import version_component_re


class Schedule(models.Model):
    work_days = models.TextField(verbose_name='Рабочие дни')
    rest_days = models.TextField(verbose_name='Выходные дни')
    start_time = models.DateTimeField(verbose_name='Начало работы')
    end_time = models.DateTimeField(verbose_name='Конец работы')
    is_working = models.BooleanField(default=True)

class Services(models.Model):
    name = models.CharField(max_length=50,  verbose_name='Название услуги')
    description = models.TextField(verbose_name='Описание услуги')
    price = models.FloatField(verbose_name='Цена')
    #doctor =

class Categories(models.Model):
    name = models.CharField(max_length=70, verbose_name='Название категории')
    description = models.TextField(verbose_name='Описании категории')
    image = models.ImageField(verbose_name='фото категории')

class Review(models.Model):
    REVIEW_CHOICES = [
        ('bad', 'плохо'),
        ('good', 'хорошо'),
        ('excellent', 'отлично' )
    ]
    #user =
    #clinic =
    text = models.TextField(max_length=100, verbose_name='Текст')
    estimation = models.CharField(max_length=15, choices=REVIEW_CHOICES, default='good', verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

class Clinics(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(max_length=200, verbose_name = 'Описание')
    location = models.TextField(max_length=50, verbose_name='Адрес')
    contact = models.IntegerField(verbose_name='Контакты')
    image = models.ImageField(verbose_name='Фото')
    logo = models.ImageField(verbose_name='Лого')
    #doctors =
    rating = models.ForeignKey(Review, on_delete=models.CASCADE, verbose_name='Рейтинг')
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, verbose_name='Категории')
    services = models.ForeignKey(Services, on_delete=models.CASCADE, verbose_name='Услуги')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='График работы')
    created_at = models.DateField(verbose_name='Дата создания')


