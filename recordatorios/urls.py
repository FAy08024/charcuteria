
from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.lista_recordatorios,
        name='lista_recordatorios'
    ),
]
