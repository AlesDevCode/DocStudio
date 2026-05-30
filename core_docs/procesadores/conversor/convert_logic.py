# core_docs/procesadores/conversor/convert_logic.py
import os
import sqlite3
from pdf2docx import Converter
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

DB_NAME = "db.sqlite3"
CARPETA_CONVERSIONES = "media/conversiones"

def inicializar_entorno_conversor():
    if not os.path.exists(CARPETA_CONVERSIONES):
        os.makedirs(CARPETA_CONVERSIONES)

def convertir_docx_a_pdf_nativo(ruta_docx, ruta_pdf):
    """Convierte un archivo .docx a .pdf de forma 100% nativa en Python sin requerir Office."""
    doc_docx = Document(ruta_docx)
    doc_pdf = SimpleDocTemplate(ruta_pdf, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    
    story = []
    for parrafo in doc_docx.paragraphs:
        if parrafo.text.strip():
            # Convertimos cada línea de Word en un bloque estructurado de ReportLab
            story.append(Paragraph(parrafo.text, style_normal))
            
    doc_pdf.build(story)

def ejecutar_conversion(file_bytes, nombre_original, direccion, ruta_salida_final):
    try:
        inicializar_entorno_conversor()
        
        # 1. Guardar temporalmente el archivo subido
        ruta_entrada_temporal = os.path.join(CARPETA_CONVERSIONES, f"temp_{nombre_original}")
        with open(ruta_entrada_temporal, "wb") as f_temp:
            for chunk in file_bytes.chunks():
                f_temp.write(chunk)

        # 2. Ejecutar la transformación según la dirección elegida
        if direccion == "pdf_to_word":
            cv = Converter(ruta_entrada_temporal)
            cv.convert(ruta_salida_final, start=0, end=None)
            cv.close()
            meta_format = "docx"
            
        elif direccion == "word_to_pdf":
            # Llamamos a nuestra función nativa que no requiere programas externos
            convertir_docx_a_pdf_nativo(ruta_entrada_temporal, ruta_salida_final)
            meta_format = "pdf"
            
        else:
            return False, f"Dirección de conversión '{direccion}' no soportada."

        # 3. Limpiar el archivo temporal inmediatamente
        if os.path.exists(ruta_entrada_temporal):
            os.remove(ruta_entrada_temporal)

        # 4. Registrar en la base de datos con formato Typst
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_original TEXT NOT NULL,
                ruta_copia TEXT NOT NULL,
                codigo_bibtex TEXT NOT NULL, 
                fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        meta_typst = f'#document(title: "{nombre_original}", format: "{meta_format}", engine: "typst")'
        
        cursor.execute("""
            INSERT INTO documentos (nombre_original, ruta_copia, codigo_bibtex)
            VALUES (?, ?, ?)
        """, (nombre_original, ruta_salida_final, meta_typst))
        
        conexion.commit()
        conexion.close()

        return True, "Conversión efectueda con éxito."

    except Exception as e:
        if 'ruta_entrada_temporal' in locals() and os.path.exists(ruta_entrada_temporal):
            try: os.remove(ruta_entrada_temporal)
            except: pass
        return False, f"Fallo técnico en la conversión: {str(e)}"