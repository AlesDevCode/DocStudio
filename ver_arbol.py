import os

def mostrar_arbol(ruta=".", prefijo=""):
    # 1. Extensiones permitidas
    extensiones_validas = {'.py', '.html', '.css', '.png', '.txt', '.md', '.sqlite3'}
    archivos_validos = {'.gitignore'}
    
    # 2. Archivos específicos de Python/Django que NO quieres ver (Opcional)
    # Si quieres verlos, simplemente sácalos de esta lista
    archivos_ignorados = {'__init__.py', 'asgi.py', 'wsgi.py'} 
    
    # 3. Carpetas del sistema, entorno virtual y caché que se ignoran por completo
    carpetas_ignoradas = {'.git', '.venv', '__pycache__', '.vscode', 'env', 'venv'}

    try:
        items = os.listdir(ruta)
    except PermissionError:
        return

    # Filtrar elementos según tus reglas
    items_filtrados = []
    for item in items:
        # Ignorar carpetas ocultas o de sistema de la lista
        if item in carpetas_ignoradas:
            continue
            
        full_path = os.path.join(ruta, item)
        
        if os.path.isdir(full_path):
            items_filtrados.append(item)
        else:
            # Ignorar archivos compilados de python (.pyc) y los específicos de la lista
            if item.endswith('.pyc') or item in archivos_ignorados:
                continue
                
            _, ext = os.path.splitext(item)
            if ext in extensiones_validas or item in archivos_validos:
                items_filtrados.append(item)

    # Ordenar: Carpetas primero, luego archivos
    items_filtrados.sort(key=lambda x: (not os.path.isdir(os.path.join(ruta, x)), x.lower()))

    # Dibujar la estructura
    for i, item in enumerate(items_filtrados):
        es_ultimo = (i == len(items_filtrados) - 1)
        simbolo = "└── " if es_ultimo else "├── "
        
        print(f"{prefijo}{simbolo}{item}")
        
        full_path = os.path.join(ruta, item)
        if os.path.isdir(full_path):
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            mostrar_arbol(full_path, nuevo_prefijo)

if __name__ == "__main__":
    print(".")
    mostrar_arbol()