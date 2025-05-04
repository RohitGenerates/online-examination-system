from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import root_view

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('exams/', include('exams.urls', namespace='exams')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)