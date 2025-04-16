from django.contrib import admin
from .models import (
    Doctor, ReviewDoctor, ScheduleDoctor, Specialization
)

admin.site.register(Doctor)
admin.site.register(ReviewDoctor)
admin.site.register(ScheduleDoctor)
admin.site.register(Specialization)
