# fairhire/apps/auth_app/models.py
# ─────────────────────────────────────────────────────────────────
#  Custom HR User model.
#  Extends Django's AbstractBaseUser for email-based login.
# ─────────────────────────────────────────────────────────────────

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class HRUserManager(BaseUserManager):
    """Custom manager for HRUser."""

    def create_user(self, email, name, password=None, **extra):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, name=name, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra):
        extra.setdefault('is_staff',     True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra)


class HRUser(AbstractBaseUser, PermissionsMixin):
    """
    HR Manager user account.
    Stored in MySQL table: auth_app_hruser
    """

    ROLE_CHOICES = [
        ('hr_manager', 'HR Manager'),
        ('admin',      'Admin'),
    ]

    email       = models.EmailField(unique=True)
    name        = models.CharField(max_length=150)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default='hr_manager')

    # Firebase Cloud Messaging token for push notifications
    # Updated every time the user logs in from Flutter app
    fcm_token   = models.TextField(blank=True, null=True)

    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects  = HRUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table    = 'hr_users'
        verbose_name = 'HR User'

    def __str__(self):
        return f'{self.name} ({self.email})'
