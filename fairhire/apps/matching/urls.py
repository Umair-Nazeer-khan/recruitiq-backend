# fairhire/apps/matching/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',         views.match_candidates, name='matching'),
    path('match/',   views.match_candidates, name='match-candidates'),
    path('results/', views.match_results,    name='match-results'),
    path('evaluations/<int:evaluation_id>/decision/', views.update_evaluation_decision, name='evaluation-decision'),
]
