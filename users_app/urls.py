from django.urls import path

from . import views


app_name = 'users_app'


urlpatterns = [
    path('sign-in/', views.sign_user_view, name='sign_user'),
    path('verify/', views.verify_user_view, name='verify_email'),
    path('logout/', views.logout_user, name='logout_user'),
]


