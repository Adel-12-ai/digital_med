from django.contrib import admin

from users_app.models import SMSVerification, User, Appointment

admin.site.register(User)
admin.site.register(SMSVerification)
admin.site.register(Appointment)
