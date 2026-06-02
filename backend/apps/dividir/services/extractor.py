# backend/apps/dividir/services/extractor.py
import os
import re
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from django.core.files.base import ContentFile
from apps.dividir.models import DocumentoUsuario, HistorialAcciones

class ExtractorPDFService:
    """
    Servicio encargado de la lógica avanzada de extracción y división de páginas de un PDF,
    e integración automática con el ORM de Django.
    """

    @staticmethod
    def _parsear_rangos(rango_texto, total_paginas):
        """
        Analiza cadenas complejas como '1-3, 5, 7-10' y devuelve una lista única de índices.
        """
        paginas_a_extraer = set() # Evitamos páginas duplicadas si el usuario repite rangos
        # Limpiamos espacios y separamos por comas
        bloques = rango_texto.replace(" ", "").split(",")

        for bloque in bloques:
            if not bloque:
                continue
            try:
                if "-" in bloque:
                    inicio_str, fin_str = bloque.split("-")
                    inicio = int(inicio_str) - 1
                    fin = int(fin_str)
                    # Validar límites del PDF
                    inicio = max(0, min(inicio, total_paginas))
                    fin = max(0, min(fin, total_paginas))
                    for p in range(inicio, fin):
                        paginas_a_extraer.add(p)
                else:
                    p = int(bloque) - 1
                    if 0 <= p < total_paginas:
                        paginas_a_extraer.add(p)
            except ValueError:
                # Si introducen caracteres inválidos, ignoramos ese bloque
                continue

        return sorted(list(paginas_a_extraer))

    @classmethod
    def ejecutar_division(cls, usuario, archivo_subido, rango_paginas):
        """
        Procesa el PDF, extrae las páginas y registra la operación en la Base de Datos vinculada al usuario.
        """
        try:
            # Leer el archivo desde la memoria o almacenamiento temporal de Django
            pdf_bytes = archivo_subido.read()
            reader = PdfReader(BytesIO(pdf_bytes))
            writer = PdfWriter()
            total_paginas = len(reader.pages)

            # Analizar el rango de páginas solicitado
            paginas_a_extraer = cls._parsear_rangos(rango_paginas, total_paginas)

            if not paginas_a_extraer:
                return False, "El rango especificado no coincide con ninguna página válida del documento."

            # Agregar las páginas seleccionadas al escritor
            for pagina in paginas_a_extraer:
                writer.add_page(reader.pages[pagina])

            # Guardar el resultado en un flujo de bytes en memoria
            buffer_salida = BytesIO()
            writer.write(buffer_salida)
            buffer_salida.seek(0)

            # Generar el nombre del nuevo archivo modificado
            nombre_base, ext = os.path.splitext(archivo_subido.name)
            nuevo_nombre = f"{nombre_base}_dividido_{rango_paginas.replace(' ', '')}{ext}"

            # --- PERSISTENCIA EN DJANGO (ORM) ---
            # 1. Creamos el registro del documento asociado al usuario
            documento = DocumentoUsuario(
                usuario=usuario,
                nombre_original=archivo_subido.name,
                tipo_operacion='DIVIDIR',
                estado='PROCESADO'
            )
            
            # 2. Guardamos el archivo físico usando el FileField de Django
            documento.archivo.save(nuevo_nombre, ContentFile(buffer_salida.getvalue()), save=True)

            # 3. Guardamos un metadato en el historial (Reemplazo del código Typst/BibTeX que tenías)
            meta_descripcion = f"Se extrajeron las páginas [{rango_paginas}] del documento original. Total páginas resultantes: {len(paginas_a_extraer)}."
            HistorialAcciones.objects.create(
                documento=documento,
                descripcion=meta_descripcion
            )

            return True, documento

        except Exception as e:
            return False, f"Error técnico durante el procesamiento: {str(e)}"