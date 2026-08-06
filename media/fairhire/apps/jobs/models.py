# fairhire/apps/jobs/models.py
from django.db import models
from fairhire.apps.auth_app.models import HRUser


class Job(models.Model):
    """
    A job posting created by an HR Manager.
    Used as input for AI candidate matching.
    """

    JOB_TYPE_CHOICES = [
        ('full_time',  'Full Time'),
        ('part_time',  'Part Time'),
        ('remote',     'Remote'),
        ('contract',   'Contract'),
        ('internship', 'Internship'),
    ]

    EDU_CHOICES = [
        ('Matric',       'Matric'),
        ('Intermediate', 'Intermediate'),
        ('BSc / BE',     'BSc / BE'),
        ('MSc / MS',     'MSc / MS'),
        ('PhD',          'PhD'),
    ]

    created_by        = models.ForeignKey(HRUser, on_delete=models.CASCADE, related_name='jobs')
    title             = models.CharField(max_length=200)
    department        = models.CharField(max_length=100, blank=True)
    location          = models.CharField(max_length=100, blank=True)
    job_type          = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')

    # Requirements
    required_skills   = models.JSONField(default=list)   # ["Flutter", "Dart", ...]
    optional_skills   = models.JSONField(default=list)   # ["Docker", ...]
    min_experience    = models.IntegerField(default=0)   # years
    education_level   = models.CharField(max_length=20, choices=EDU_CHOICES, default='BSc / BE')
    salary_min        = models.IntegerField(null=True, blank=True)
    salary_max        = models.IntegerField(null=True, blank=True)

    # AI matching weights (must sum to 1.0)
    skill_weight      = models.FloatField(default=0.5)
    experience_weight = models.FloatField(default=0.3)
    education_weight  = models.FloatField(default=0.2)

    is_active         = models.BooleanField(default=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.department}'
