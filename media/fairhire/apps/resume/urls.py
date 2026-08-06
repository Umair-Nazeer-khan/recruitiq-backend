# fairhire/apps/resume/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',              views.list_candidates,  name='list-candidates'),
    path('upload/',       views.upload_resume,    name='upload-resume'),
    path('stats/',        views.dashboard_stats,  name='dashboard-stats'),
    path('<int:pk>/',     views.candidate_detail, name='candidate-detail'),
    path('<int:pk>/status/', views.update_status, name='update-status'),
]
