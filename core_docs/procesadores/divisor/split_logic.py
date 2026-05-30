# core_docs/procesadores/divisor/split_logic.py
import os
import sqlite3
from pypdf import PdfReader, PdfWriter

# Cambiamos a db.sqlite3 para unificar la persistencia
DB_NAME = "db.sqlite3"
CARPETA_COPIAS = "media/divisiones"

def inicializar_tabla_divisor():
    if not os.path.exists(CARPETA_COPIAS):
        os.makedirs(CARPETA_COPIAS)
        
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
    conexion.commit()
    conexion.close()

def ejecutar_division_pdf(file_bytes, nombre_original, rango_paginas, ruta_salida_pdf):
    try:
        inicializar_tabla_divisor()
        
        reader = PdfReader(file_bytes)
        writer = PdfWriter()
        total_paginas = len(reader.pages)
        paginas_a_extraer = []

        rango_paginas = rango_paginas.strip()
        if "-" in rango_paginas:
            inicio, fin = rango_paginas.split("-")
            for p in range(int(inicio) - 1, int(fin)):
                if 0 <= p < total_paginas:
                    paginas_a_extraer.append(p)
        elif "," in rango_paginas:
            for item in rango_paginas.split(","):
                p = int(item.strip()) - 1
                if 0 <= p < total_paginas:
                    paginas_a_extraer.append(p)
        else:
            p = int(rango_paginas) - 1
            if 0 <= p < total_paginas:
                paginas_a_extraer.append(p)

        if not paginas_a_extraer:
            return False, "El rango especificado no coincide con las páginas del documento."

        for pagina in paginas_a_extraer:
            writer.add_page(reader.pages[pagina])

        with open(ruta_salida_pdf, "wb") as f_out:
            writer.write(f_out)

        # Conexión a la base de datos unificada de Django
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        # Formateamos el metadato del corte usando funciones nativas de Typst
        meta_typst = f'#pdf_split(title: "{nombre_original}", pages: "{rango_paginas}", engine: "typst")'
        
        cursor.execute("""
            INSERT INTO documentos (nombre_original, ruta_copia, codigo_bibtex)
            VALUES (?, ?, ?)
        """, (nombre_original, ruta_salida_pdf, meta_typst))
        
        conexion.commit()
        conexion.close()

        return True, "Archivo procesado con éxito."

    except Exception as e:
        return False, f"Error durante el procesamiento técnico: {str(e)}"