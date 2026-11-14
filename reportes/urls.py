
from django.urls import path
from . import views

urlpatterns = [
    path(
        'historial/demo/',
        views.historial_demo,
        name='historial_demo'
    ),

    path(
        'financiero/demo/',
        views.reporte_financiero_demo,
        name='reporte_financiero_demo'
    ),
]
