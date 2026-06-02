# historial_usuario.py
from django.db import models
from django.contrib.auth.models import User

class HistorialCambiosUsuario(models.Model):
    """Guarda el registro de qué cambió en el usuario, qué valor tenía antes y cuándo"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial_cambios')
    campo_modificado = models.CharField(max_length=100)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_nuevo = models.TextField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cambio en {self.usuario.username} ({self.campo_modificado}) - {self.fecha_modificacion}"

    class Meta:
        verbose_name = "Historial de Cambio de Usuario"
        verbose_name_plural = "Historial de Cambios de Usuarios"