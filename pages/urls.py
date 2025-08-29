"""Module for improved password recovery pages"""
from django.contrib.auth import views as auth_views # pylint: disable=unused-import
from django.urls import path


from . import views

# SECURITY FLAW 4: Identification and Authentication Failures 
# Fix here by
# disable this line by commenting it out
# path("changepswd/", views.changepswd, name="changepswd"),

# SECURITY FLAW 5: Security Misconfiguration
# Fix here by
# disable this line by commenting it out
# path("forgot/", views.forgot, name="forgot"),

urlpatterns = [
    path("", views.index, name="index"),
    path("booking/", views.booking, name="booking"),
    path("forgot/", views.forgot, name="forgot"),
    path("appointments/", views.appointments, name="appointments"),
    path("question/", views.question, name="question"),
    path("changepswd/", views.changepswd, name="changepswd"),

    path('password_reset/', auth_views.PasswordResetView.as_view(),
     name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
     name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
     name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
     name='password_reset_complete'),
]
