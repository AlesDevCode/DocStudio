from django.db import models
from .documento import DocumentoUsuario

class DescargasDocumentos(models.Model):
    """Controla cuántas veces el usuario ha bajado su PDF procesado"""
    documento = models.ForeignKey(DocumentoUsuario, on_delete=models.CASCADE, related_name='descargas')
    fecha_descarga = models.DateTimeField(auto_now_add=True)
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Descarga de {self.documento.nombre_original} el {self.fecha_descarga}"
        
    class Meta:
        verbose_name = "Registro de Descarga"
        verbose_name_plural = "Registro de Descargas"