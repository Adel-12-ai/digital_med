from django.urls import path
from . import views


app_name = 'clinic_app'

urlpatterns = [
    path('', views.home_view, name='home'),
]
