# backend/core_docs/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

# Le dice a Django qué archivo de settings usar al arrancar
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_docs.settings')

application = get_wsgi_application()