from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class DocumentoUsuario(models.Model):
    TIPO_ACCION = [
        ('DIVIDIR', 'Dividir PDF'),
        ('CONVERTIR', 'Convertir a Word'),
        ('EDITAR', 'Editar PDF'),
    ]
    
    ESTADO_PROCESO = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESADO', 'Procesado con Éxito'),
        ('ERROR', 'Error en Procesamiento'),
    ]

    VISIBILIDAD = [
        ('PRIVADO', 'Solo yo'),
        ('PUBLICO', 'Público (Visible en la comunidad)'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mis_documentos')
    nombre_original = models.CharField(max_length=255, db_index=True)
    archivo = models.FileField(
        upload_to='documentos_usuarios/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    ) 
    tipo_operacion = models.CharField(max_length=20, choices=TIPO_ACCION)
    estado = models.CharField(max_length=20, choices=ESTADO_PROCESO, default='PENDIENTE')
    privacidad = models.CharField(max_length=10, choices=VISIBILIDAD, default='PRIVADO')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_original} ({self.usuario.username}) - {self.privacidad}"

    class Meta:
        verbose_name = "Documento de Usuario"
        verbose_name_plural = "Documentos de Usuarios"