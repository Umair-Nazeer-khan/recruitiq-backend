# fairhire/apps/matching/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('match/',   views.match_candidates, name='match-candidates'),
    path('results/', views.match_results,    name='match-results'),
]
