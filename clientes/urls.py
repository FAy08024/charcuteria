
from django.urls import path
from . import views

urlpatterns = [
    path(
        'demo/',
        views.lista_clientes_demo,
        name='clientes_demo'
    ),
    path(
        'demo/<int:cliente_id>/',
        views.detalle_cliente_demo,
        name='cliente_demo_detalle'
    ),
    path(
        'crear/',
        views.crear_cliente,
        name='crear_cliente'
    ),
    path(
        'editar/<int:cliente_id>/',
        views.editar_cliente,
        name='editar_cliente'
    ),
    path(
        'estado/<int:cliente_id>/',
        views.cambiar_tipo_estado,
        name='cambiar_tipo_estado'
    ),
]

