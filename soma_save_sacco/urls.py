
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('somasavesaccosuperadmin/', admin.site.urls),
    path('client-admin/', include('adminapp.urls')),
    path('', include('clients_portal.urls')),
    path('pwa/', include('pwa.urls')),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)