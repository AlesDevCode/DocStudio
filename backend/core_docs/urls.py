# backend/core_docs/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración preinstalado de Django
    path('admin/', admin.site.urls),
    
    # Conectamos las rutas de tu aplicación "dividir" a la raíz del sitio
    path('', include('apps.dividir.urls')),
]

# Esto permite que los PDFs procesados que se guarden en /media/ puedan descargarse localmente
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)