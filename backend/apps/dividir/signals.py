# backend/apps/dividir/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import PerfilUsuario, HistorialCambiosUsuario

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Escucha cuando un usuario es creado y le genera su PerfilUsuario automáticamente"""
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(pre_save, sender=User)
def auditar_cambios_usuario(sender, instance, **kwargs):
    """Detecta si se cambiaron datos críticos del usuario antes de guardar"""
    if instance.pk:  # Si el usuario ya existe en la BD (es una actualización)
        usuario_anterior = User.objects.get(pk=instance.pk)
        
        # Campos que queremos auditar
        campos_a_revisar = ['username', 'email', 'is_active']
        
        for campo in campos_a_revisar:
            valor_viejo = getattr(usuario_anterior, campo)
            valor_nuevo = getattr(instance, campo)
            
            if valor_viejo != valor_nuevo:
                HistorialCambiosUsuario.objects.create(
                    usuario=instance,
                    campo_modificado=f"User.{campo}",
                    valor_anterior=str(valor_viejo),
                    valor_nuevo=str(valor_nuevo)
                )