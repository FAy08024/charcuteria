
from django.urls import path
from . import views

urlpatterns = [
    path(
        'demo/',
        views.inventario_demo,
        name='inventario_demo'
    ),

    
    path(
        'mi-almacen/',
        views.mi_almacen,
        name='mi_almacen'
    ),

   
    path(
        'incidencias/',
        views.incidencias_admin,
        name='inventario_incidencias'
    ),

   
    path(
        'incidencias/<int:incidencia_id>/resolver/',
        views.resolver_incidencia,
        name='resolver_incidencia'
    ),

]
