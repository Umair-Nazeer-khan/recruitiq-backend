# fairhire/apps/auth_app/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/',   views.register,   name='register'),
    path('login/',      views.login,       name='login'),
    path('logout/',     views.logout,      name='logout'),
    path('profile/',    views.profile,     name='profile'),
    path('update-fcm/', views.update_fcm,  name='update-fcm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
