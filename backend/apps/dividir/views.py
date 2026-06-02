# backend/apps/dividir/views.py
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from apps.dividir.models import DocumentoUsuario, PerfilUsuario, HistorialCambiosUsuario

# Importamos correctamente desde la nueva estructura modular
from apps.dividir.models import DocumentoUsuario, PerfilUsuario
from apps.dividir.services.extractor import ExtractorPDFService
from django.http import FileResponse

def inicio(request):
    """
    Página principal de DocStudio.
    Envía los documentos recientes del usuario logueado bajo la variable 'recientes'
    y también los documentos públicos de la comunidad.
    """
    contexto = {
        'recientes': None,
        'documentos_publicos': DocumentoUsuario.objects.filter(estado='PROCESADO', privacidad='PUBLICO').order_by('-fecha_subida')[:10] # Trae los últimos 10 públicos globalmente
    }
    
    if request.user.is_authenticated:
        # Traemos el historial específico del usuario logueado
        contexto['recientes'] = DocumentoUsuario.objects.filter(usuario=request.user).order_by('-fecha_subida')

    return render(request, 'inicio.html', contexto)


@login_required
def panel_usuario(request):
    """Redirección alternativa de seguridad al panel principal."""
    return redirect('inicio')


@login_required
def dividir_pdf_view(request):
    if request.method == "POST":
        archivo = request.FILES.get("mi_pdf")
        rango = request.POST.get("paginas")
        privacidad_elegida = request.POST.get("privacidad", "PRIVADO")

        if not archivo or not rango:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'dividir.html')

        # El servicio ejecuta la división y guarda el archivo en Media
        exito, resultado = ExtractorPDFService.ejecutar_division(
            usuario=request.user, 
            archivo_subido=archivo, 
            rango_paginas=rango
        )

        if exito:
            # 'resultado' es la instancia de DocumentoUsuario
            resultado.privacidad = privacidad_elegida
            resultado.save()

            # --- NUEVA LÓGICA DE DESCARGA DIRECTA ---
            try:
                # Abrimos el archivo guardado en el FileField de Django
                response = FileResponse(resultado.archivo.open('rb'), content_type='application/pdf')
                
                # 'as_attachment=True' le dice al navegador que lo descargue en vez de abrirlo
                response['Content-Disposition'] = f'attachment; filename="{resultado.archivo.name.split("/")[-1]}"'
                return response
            except Exception as e:
                messages.error(request, f"El PDF se procesó pero no se pudo descargar: {e}")
                return redirect('inicio')
        else:
            messages.error(request, resultado)
            return render(request, 'dividir.html')

    return render(request, 'dividir.html')

def registro_view(request):
    """Maneja el registro capturando los datos del perfil extendido"""
    if request.user.is_authenticated:
        return redirect('inicio')
        
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        foto = request.FILES.get("foto")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return render(request, 'registro.html')

        # Crear el usuario base de Django (esto activa la señal automáticamente)
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Obtenemos el perfil creado por la señal para meterle los nuevos campos
        perfil = user.perfil
        perfil.fecha_nacimiento = fecha_nacimiento
        if foto:
            perfil.foto = foto
        perfil.save()

        login_user(request, user)
        return redirect('inicio')

    return render(request, 'registro.html')


@login_required
def perfil_ver_view(request):
    # Buscamos todos los documentos creados por el usuario logueado
    mis_documentos = DocumentoUsuario.objects.filter(usuario=request.user).order_by('-fecha_subida')
    
    contexto = {
        'mis_documentos': mis_documentos
    }
    return render(request, 'perfil_ver.html', contexto)


@login_required
def perfil_ajustes_view(request):
    """Procesa de forma única las modificaciones de campos permitidos y muestra el historial de PDFs"""
    # 🛠️ SOLUCIÓN: Si el usuario no tiene perfil en la BD, lo creamos de inmediato de forma segura.
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        biografia = request.POST.get("biografia", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", None)
        nueva_foto = request.FILES.get("foto")

        if not username or not email:
            messages.error(request, "El nombre de usuario y correo son obligatorios.")
            return redirect('perfil_ajustes')

        if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
            messages.error(request, f"El nombre de usuario '{username}' ya está en uso.")
            return redirect('perfil_ajustes')

        try:
            # Actualizamos datos del User (Se dispara la señal pre_save automáticamente de auditoría)
            request.user.username = username
            request.user.email = email
            request.user.save()

            # Actualizamos datos del Perfil
            perfil.biografia = biografia
            if fecha_nacimiento:
                perfil.fecha_nacimiento = fecha_nacimiento
            else:
                perfil.fecha_nacimiento = None

            if nueva_foto:
                perfil.foto = nueva_foto

            perfil.save() # Al guardar, auto_now actualiza 'ultima_modificacion' automáticamente

            messages.success(request, "¡Tus ajustes han sido guardados con éxito!")
            return redirect('perfil_ver') # Redireccionamos a la vista de visualización para ver el resultado

        except Exception as e:
            messages.error(request, f"Error al actualizar el perfil: {e}")
            return redirect('perfil_ajustes')

    # Si es GET, cargamos únicamente sus documentos para la sección inferior de la página de ajustes
    mis_documentos = DocumentoUsuario.objects.filter(usuario=request.user).order_by('-fecha_subida')
    return render(request, 'perfil_ajustes.html', {'mis_documentos': mis_documentos})

def login_view(request):
    """Maneja el acceso de usuarios controlando cuentas activas/desactivadas."""
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        usuario = request.POST.get('username', '').strip()
        clave = request.POST.get('password', '').strip()
        
        if not usuario or not clave:
            messages.error(request, "Por favor, completa todos los campos.")
            return render(request, 'login.html')
            
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            # Control estricto: Si el admin lo desactivó (is_active=False), no entra
            if not user.is_active:
                messages.error(request, "Esta cuenta se encuentra temporalmente desactivada.")
                return render(request, 'login.html')
                
            login_user(request, user)
            return redirect('inicio')
        else:
            messages.error(request, "Credenciales incorrectas. Inténtalo de nuevo.")
            return render(request, 'login.html')
            
    return render(request, 'login.html')


def logout_view(request):
    """Cierra la sesión actual de manera segura."""
    logout_user(request)
    return redirect('login')

def lista_comunidad(request):
    """Muestra todos los usuarios registrados y activos de DocStudio."""
    usuarios_comunidad = User.objects.filter(is_active=True).exclude(is_superuser=True).select_related('perfil')
    return render(request, 'comunidad.html', {'usuarios': usuarios_comunidad})


def perfil_publico(request, username):
    """Muestra los datos públicos y PDFs públicos de un usuario específico."""
    user_objetivo = get_object_or_404(User, username=username, is_active=True)
    
    # Filtramos estrictamente solo sus documentos procesados y que sean PUBLICOS
    docs_publicos = user_objetivo.mis_documentos.filter(estado='PROCESADO', privacidad='PUBLICO').order_by('-fecha_subida')
    
    contexto = {
        'perfil_user': user_objetivo,
        'archivos_publicos': docs_publicos
    }
    return render(request, 'perfil_ver.html', contexto)

@login_required
@require_POST
def cambiar_privacidad_documento(request, doc_id):
    """Cambia dinámicamente el estado de privacidad de un PDF de público a privado o viceversa"""
    # Buscamos el documento asegurándonos de que pertenezca al usuario logueado por seguridad
    documento = get_object_or_404(DocumentoUsuario, id=doc_id, usuario=request.user)
    
    # Alternamos el estado
    if documento.privacidad == 'PRIVADO':
        documento.privacidad = 'PUBLICO'
        messages.success(request, f"El documento '{documento.nombre_original}' ahora es Público 🌐.")
    else:
        documento.privacidad = 'PRIVADO'
        messages.success(request, f"El documento '{documento.nombre_original}' ahora es Privado 🔒.")
        
    documento.save()
    return redirect('perfil_ajustes')
