from django.db import models

from fairhire.apps.jobs.models import Job
from fairhire.apps.resume.models import Candidate


class CandidateEvaluation(models.Model):
    EVALUATION_STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('evaluated', 'Evaluated'),
        ('failed', 'Failed'),
    ]
    DECISION_STATUS_CHOICES = [
        ('new', 'New'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('on_hold', 'On Hold'),
    ]

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='job_evaluations',
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='candidate_evaluations',
    )
    evaluation_status = models.CharField(
        max_length=20,
        choices=EVALUATION_STATUS_CHOICES,
        default='processing',
    )
    decision_status = models.CharField(
        max_length=20,
        choices=DECISION_STATUS_CHOICES,
        default='new',
    )
    match_score = models.FloatField(null=True, blank=True)
    skill_score = models.FloatField(null=True, blank=True)
    experience_score = models.FloatField(null=True, blank=True)
    education_score = models.FloatField(null=True, blank=True)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    explanation = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['candidate', 'job'],
                name='unique_candidate_job_evaluation',
            ),
        ]

    def __str__(self):
        return f'{self.candidate} — {self.job}'