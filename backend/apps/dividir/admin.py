# backend/apps/dividir/admin.py
from django.contrib import admin
# Importamos HistorialCambiosUsuario desde el __init__.py unificado
from .models import DocumentoUsuario, PerfilUsuario, HistorialAcciones, DescargasDocumentos, HistorialCambiosUsuario

@admin.register(DocumentoUsuario)
class DocumentoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_original', 'usuario', 'tipo_operacion', 'estado', 'fecha_subida')
    list_filter = ('tipo_operacion', 'estado', 'fecha_subida')
    search_fields = ('nombre_original', 'usuario__username')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    # Añadimos 'ultima_modificacion' al panel para monitoreo rápido
    list_display = ('usuario', 'limite_diario', 'fecha_nacimiento', 'ultima_modificacion')
    search_fields = ('usuario__username',)

@admin.register(HistorialAcciones)
class HistorialAccionesAdmin(admin.ModelAdmin):
    list_display = ('documento', 'descripcion', 'fecha_accion')
    search_fields = ('documento__nombre_original', 'descripcion')

@admin.register(DescargasDocumentos)
class DescargasDocumentosAdmin(admin.ModelAdmin):
    list_display = ('documento', 'fecha_descarga', 'ip_usuario')

# Nuevo registro para la auditoría de usuarios
@admin.register(HistorialCambiosUsuario)
class HistorialCambiosUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'campo_modificado', 'valor_anterior', 'valor_nuevo', 'fecha_modificacion')
    list_filter = ('campo_modificado', 'fecha_modificacion')
    search_fields = ('usuario__username', 'campo_modificado')