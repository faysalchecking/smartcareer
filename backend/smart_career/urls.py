"""
URL configuration for SMART CAREER project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('smart_career.apps.authentication.urls')),
    path('api/candidates/', include('smart_career.apps.candidates.urls')),
    path('api/jobs/', include('smart_career.apps.jobs.urls')),
    path('api/applications/', include('smart_career.apps.applications.urls')),
    path('api/documents/', include('smart_career.apps.documents.urls')),
    path('api/medical/', include('smart_career.apps.medical.urls')),
    path('api/visa/', include('smart_career.apps.visa.urls')),
    path('api/tasks/', include('smart_career.apps.tasks.urls')),
    path('api/alerts/', include('smart_career.apps.alerts.urls')),
    path('api/notifications/', include('smart_career.apps.notifications.urls')),
    path('api/agents/', include('smart_career.apps.agents.urls')),
    path('api/clients/', include('smart_career.apps.clients.urls')),
    path('api/finance/', include('smart_career.apps.finance.urls')),
    path('api/ai/', include('smart_career.apps.ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)