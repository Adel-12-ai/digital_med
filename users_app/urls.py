from django.urls import path

from . import views


app_name = 'users_app'


urlpatterns = [
    path('sign-in/', views.sign_user_view, name='sign_user'),
    path('verify/', views.verify_user_view, name='verify_email'),
    path('logout/', views.logout_user, name='logout_user'),

    path('send_appointment/', views.AppointmentCreateView.as_view(), name='send_appointment'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),
    path('appointment/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment'),
    path('appointment_update/<int:pk>/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    path('appointment_delete/<int:pk>/', views.AppointmentDeleteView.as_view(), name='appointment_delete'),

    path('get-doctors/', views.get_doctors, name='get_doctors'),
]


