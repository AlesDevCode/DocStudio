# backend/apps/dividir/admin.py
from django.contrib import admin
from .models import historial
from .models import opciones

# Registramos el modelo en el panel administrador
admin.site.register(historial)
admin.site.register(opciones)