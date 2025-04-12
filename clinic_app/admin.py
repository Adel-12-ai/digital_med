from django.contrib import admin
from .models import(
    Clinic, Category, ScheduleClinic, Service,
    ReviewClinic, WeekDay,
)

admin.site.register(Clinic)
admin.site.register(Category)
admin.site.register(ScheduleClinic)
admin.site.register(Service)
admin.site.register(ReviewClinic)
admin.site.register(WeekDay)