# backend/apps/dividir/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('panel/', views.panel_usuario, name='panel_usuario'),
    path('dividir/', views.dividir_pdf_view, name='dividir_pdf'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('comunidad/', views.lista_comunidad, name='comunidad'),
    path('comunidad/perfil/<str:username>/', views.perfil_publico, name='perfil_publico'),
    
    # --- NUEVAS VISTAS SEPARADAS DE PERFIL ---
    path('perfil/', views.perfil_ver_view, name='perfil_ver'), 
    path('configuracion/', views.perfil_ajustes_view, name='perfil_ajustes'), 
    
    path('documento/privacidad/<int:doc_id>/', views.cambiar_privacidad_documento, name='cambiar_privacidad'),
]