
from django.urls import path
from . import views

urlpatterns = [
    path(
        'demo/',
        views.cuentas_demo,
        name='cuentas_demo'
    ),
    path(
        'demo/<int:cliente_id>/',
        views.detalle_cuenta_demo,
        name='detalle_cuenta_demo'
    ),

path('abonos/registrar/', views.registrar_abono, name='registrar_abono'),

]
