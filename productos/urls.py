
from django.urls import path
from . import views

urlpatterns = [
    path(
        'demo/',
        views.productos_demo,
        name='productos_demo'
    ),

    path(
        'crear/',
        views.crear_producto,
        name='crear_producto'
    ),

    path(
        'editar/<int:pk>/',
        views.editar_producto,
        name='editar_producto'
    ),
    path(
    'combos/crear/',
    views.crear_combo,
    name='crear_combo'
    ),
]
