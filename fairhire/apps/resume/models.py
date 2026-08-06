# fairhire/apps/resume/models.py
# ─────────────────────────────────────────────────────────────────
#  Resume and Candidate models.
#  Stores parsed resume data extracted by AI.
# ─────────────────────────────────────────────────────────────────

from django.db import models
from fairhire.apps.auth_app.models import HRUser


def resume_upload_path(instance, filename):
    """Store resumes in media/resumes/{user_id}/{filename}"""
    return f'resumes/{instance.uploaded_by.id}/{filename}'


class Candidate(models.Model):
    """
    One candidate = one uploaded resume.
    Parsed fields are filled by the AI engine after upload.
    """

    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('accepted',    'Accepted'),
        ('rejected',    'Rejected'),
        ('on_hold',     'On Hold'),
    ]

    # Who uploaded this resume
    uploaded_by   = models.ForeignKey(HRUser, on_delete=models.CASCADE, related_name='candidates')

    # Original file
    resume_file   = models.FileField(upload_to=resume_upload_path)
    original_name = models.CharField(max_length=255)  # original filename

    # ── Parsed fields (filled by AI) ─────────────────────────────
    name              = models.CharField(max_length=200, blank=True)
    email             = models.EmailField(blank=True)
    phone             = models.CharField(max_length=30, blank=True)
    location          = models.CharField(max_length=100, blank=True)
    education         = models.TextField(blank=True)   # e.g. "BSc Computer Science, FAST"
    education_level   = models.CharField(max_length=50, blank=True)  # e.g. "BSc", "MSc"
    experience_years  = models.FloatField(default=0)
    skills            = models.JSONField(default=list)       # ["Python", "Flutter", ...]
    work_history      = models.JSONField(default=list)       # [{company, role, duration}, ...]
    raw_text          = models.TextField(blank=True)         # full resume text

    # ── Match results ─────────────────────────────────────────────
    match_score       = models.FloatField(null=True, blank=True)
    skill_score       = models.FloatField(null=True, blank=True)
    experience_score  = models.FloatField(null=True, blank=True)
    education_score   = models.FloatField(null=True, blank=True)
    missing_skills    = models.JSONField(default=list)
    score_explanation = models.TextField(blank=True)  # TRANSPARENCY FEATURE

    # ── HR decision ───────────────────────────────────────────────
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_notes          = models.TextField(blank=True)

    # ── Timestamps ────────────────────────────────────────────────
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'candidates'
        ordering  = ['-created_at']

    def __str__(self):
        return f'{self.name or self.original_name}'
