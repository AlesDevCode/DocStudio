# core_docs/views.py
import os
from django.shortcuts import render
from django.http import FileResponse
from django.contrib import messages
from django.conf import settings

# CORRECCIÓN DE LA RUTA: Apuntando a la ubicación interna dentro de core_docs
from core_docs.procesadores.divisor.split_logic import ejecutar_division_pdf
from core_docs.procesadores.conversor.convert_logic import ejecutar_conversion

def dividir_pdf_view(request):
    if request.method == "POST":
        archivo = request.FILES.get("mi_pdf")
        rango = request.POST.get("paginas")
        
        if not archivo or not rango:
            messages.error(request, "Por favor, completa todos los campos del formulario.")
            return render(request, "core_docs/dividir.html")
        
        # Aseguramos la existencia del directorio multimedia en la raíz
        directorio_salida = os.path.join(settings.BASE_DIR, "media", "copias_pdf")
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
            
        nombre_salida = f"split_{archivo.name}"
        ruta_completa_salida = os.path.join(directorio_salida, nombre_salida)
        
        # Invocación del backend modular
        exito, resultado = ejecutar_division_pdf(
            file_bytes=archivo,
            nombre_original=archivo.name,
            rango_paginas=rango,
            ruta_salida_pdf=ruta_completa_salida
        )
        
        if exito:
            try:
                response = FileResponse(open(ruta_completa_salida, 'rb'), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{nombre_salida}"'
                return response
            except Exception as e:
                messages.error(request, f"Error al generar la descarga: {e}")
        else:
            messages.error(request, f"Error: {resultado}")

    return render(request, "core_docs/dividir.html")

def vista_inicio(request):
    return render(request, "core_docs/inicio.html")

def vista_conversor(request):
    if request.method == "POST":
        archivo = request.FILES.get("mi_archivo")
        direccion = request.POST.get("direccion")  # Recibe 'pdf_to_word' o 'word_to_pdf'
        
        if not archivo or not direccion:
            messages.error(request, "Por favor, selecciona un archivo válido y el tipo de conversión.")
            return render(request, 'core_docs/conversor.html')
        
        directorio_salida = os.path.join(settings.BASE_DIR, "media", "conversiones")
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
            
        nombre_base, _ = os.path.splitext(archivo.name)
        
        # Configurar salida dinámica de archivos y tipos de contenido
        if direccion == "pdf_to_word":
            nombre_salida = f"{nombre_base}.docx"
            content_type_download = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            nombre_salida = f"{nombre_base}.pdf"
            content_type_download = "application/pdf"
            
        ruta_completa_salida = os.path.join(directorio_salida, nombre_salida)
        
        exito, resultado = ejecutar_conversion(
            file_bytes=archivo,
            nombre_original=archivo.name,
            direccion=direccion,
            ruta_salida_final=ruta_completa_salida
        )
        
        if exito:
            try:
                response = FileResponse(open(ruta_completa_salida, 'rb'), content_type=content_type_download)
                response['Content-Disposition'] = f'attachment; filename="{nombre_salida}"'
                return response
            except Exception as e:
                messages.error(request, f"Error al descargar el archivo generado: {e}")
        else:
            messages.error(request, f"Error en la conversión: {resultado}")

    return render(request, 'core_docs/conversor.html')