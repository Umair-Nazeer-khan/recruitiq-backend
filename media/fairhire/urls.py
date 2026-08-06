# fairhire/urls.py
# ─────────────────────────────────────────────────────────────────
#  Main URL configuration.
#  All API routes are prefixed with /api/v1/
# ─────────────────────────────────────────────────────────────────

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def home(request):
    return HttpResponse(
        "Fairhire API is running. Available routes: /api/v1/auth/, /api/v1/resumes/, /api/v1/jobs/, /api/v1/matching/"
    )

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),

    # ── API v1 routes ──────────────────────────────────────────
    path('api/v1/auth/',     include('fairhire.apps.auth_app.urls')),
    path('api/v1/resumes/',  include('fairhire.apps.resume.urls')),
    path('api/v1/jobs/',     include('fairhire.apps.jobs.urls')),
    path('api/v1/matching/', include('fairhire.apps.matching.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
