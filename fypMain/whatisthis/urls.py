"""whatisthis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views
from .views import * #import all functions from views.py
from django.conf import settings
from django.conf.urls.static import static
from .views import ResetPasswordView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', home, name = "home"),
    path('login/', views.Login.as_view(), name='login'),#login page
    path("signup/", views.SignUp.as_view(), name="signup"),#signup page
    path('upload_image', upload_image, name='upload_image'),#main function page(from start button)
    path('menu', menu, name='menu'),#main menu
    path('user', user, name='user'),#view/edit user account
    path('gallery', gallery, name='gallery'), #image gallery
    path('delete_image', delete_image, name='delete_image'),#used to invoke image delete by passing image ID
    path('delete_user', delete_user, name='delete_user'),#confirmation page for delete user
    path('tasks', manage_tasks, name = 'tasks'),#view/create tasks
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),#password reset form
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),#password reset confirmation
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),#password reset success page
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),#edit password form
    path('logout', auth_views.LogoutView.as_view(), name='logout')#logout redirect to login
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()