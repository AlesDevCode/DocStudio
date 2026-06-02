from django.db import models
from .documento import DocumentoUsuario

class HistorialAcciones(models.Model):
    """Registra detalladamente qué se le hizo al PDF"""
    documento = models.ForeignKey(DocumentoUsuario, on_delete=models.CASCADE, related_name='historial')
    descripcion = models.TextField()
    fecha_accion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Acción en {self.documento.nombre_original} - {self.fecha_accion}"
        
    class Meta:
        verbose_name = "Historial de Acción"
        verbose_name_plural = "Historial de Acciones"