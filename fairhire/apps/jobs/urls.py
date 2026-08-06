# fairhire/apps/jobs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',          views.job_list_create, name='job-list-create'),
    path('<int:pk>/', views.job_detail,      name='job-detail'),
]
