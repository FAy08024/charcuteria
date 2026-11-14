
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
]
