from django.urls import path
from . import views


app_name = 'clinic_app'

urlpatterns = [
    path('', views.clinic_view),
    path('<int:clinic_id>/', views.clinic_detail_view, name='detail'),
    path('clinic_view/', views.clinic_detail_view)
]
