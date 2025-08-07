from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import root_view
from exams.views import api_student_exams, api_student_results
from exams.urls import view_patterns

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    
    # View URLs (non-API)
    path('exams/', include((view_patterns, 'exams'))),  # Regular views under /exams/
    # API URLs (add this line)
    path('exams/', include('exams.urls')),  # Include API endpoints under /exams/
    
    # API URLs - include all exam API endpoints under /api/exams/
    path('api/exams/', include('exams.urls_api')),
    
    # Additional API endpoints
    path('api/student/exams', api_student_exams, name='api_student_exams'),
    path('api/student/results', api_student_results, name='api_student_results'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Also serve from STATICFILES_DIRS
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)