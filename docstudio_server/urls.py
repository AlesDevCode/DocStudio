from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Aquí es donde faltaba la 's'
    path('admin/', admin.site.urls), 
    
    path('', include('core_docs.urls')),
]