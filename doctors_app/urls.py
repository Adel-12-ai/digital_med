from django.urls import path

from . import views


app_name = 'doctors_app'


urlpatterns = [
    path('doctors/', views.DoctorListView.as_view(), name='doctors'),
    path('doctor/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor'),

    path('appointments/', views.AppointmentsListView.as_view(), name='appointments'),
    path('appointment/<int:pk>/', views.AppointmentsDetailView.as_view(), name='appointment'),
]


