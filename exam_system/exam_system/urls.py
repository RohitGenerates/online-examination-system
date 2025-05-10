from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import root_view
from exams.views import api_student_exams, api_student_results

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    
    # View URLs (non-API)
    path('exams/', include('exams.urls', namespace='exams_views')),
    
    # API URLs
    path('api/exams/', include('exams.urls', namespace='exams_api')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Also serve from STATICFILES_DIRS
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)