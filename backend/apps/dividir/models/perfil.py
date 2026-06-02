import os
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.templatetags.static import static
from django.conf import settings

def ruta_perfil(instance, filename):
    """Genera una ruta única para la foto de perfil de cada usuario"""
    ext = filename.split('.')[-1]
    return f'perfiles/user_{instance.usuario.id}.{ext}'

class PerfilUsuario(models.Model):
    """Extiende el modelo User de Django con metadatos personalizados"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto = models.ImageField(upload_to=ruta_perfil, blank=True, null=True)
    biografia = models.TextField(max_length=500, blank=True)
    limite_diario = models.IntegerField(default=20, validators=[MinValueValidator(0)])
    
    fecha_nacimiento = models.DateField(null=True, blank=True, help_text="Para calcular la edad de forma dinámica")
    ultima_modificacion = models.DateTimeField(auto_now=True, help_text="Se actualiza automáticamente en cada cambio")

    @property
    def edad(self):
        """Calcula la edad actual en base a la fecha de nacimiento de forma dinámica"""
        if self.fecha_nacimiento:
            hoy = date.today()
            return hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None
    
    @property
    def obtener_foto_url(self):
        """Devuelve la URL de la foto si existe, de lo contrario devuelve None"""
        if self.foto and hasattr(self.foto, 'url'):
            try:
                return self.foto.url
            except ValueError:
                pass
        return None  # <--- Si no hay foto, dejamos que el HTML decida qué poner

    def __str__(self):
        estado_cuenta = "Activo" if self.usuario.is_active else "Inactivo/Baneado"
        return f"Perfil de {self.usuario.username} ({estado_cuenta})"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"