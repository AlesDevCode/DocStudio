from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_inicio, name='inicio'), # Raíz ahora cargará el inicio
    path('inicio/', views.vista_inicio, name='inicio'),
    path('dividir/', views.dividir_pdf_view, name='dividir_pdf'),
   path('conversor/', views.vista_conversor, name='conversor'),
]
