from django.urls import path
from . import views


app_name = 'clinic_app'


urlpatterns = [
    path('', views.ClinicListView.as_view(), name='clinics'),
    path('clinic/<int:pk>/', views.ClinicDetailView.as_view(), name='clinic'),
]
