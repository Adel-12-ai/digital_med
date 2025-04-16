from django.urls import path
from . import views

app_name = 'clinic_app'

urlpatterns = [
    path('', views.ClinicListView.as_view(), name='clinics'),
    path('clinic/<int:pk>/', views.ClinicDetailView.as_view(), name='clinic'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),

    path('services/', views.ServicesListView.as_view(), name='services'),
    path('service/<int:pk>/', views.ServicesDetailView.as_view(), name='service'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
]