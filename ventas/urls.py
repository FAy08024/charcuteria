
from django.urls import path
from . import views

urlpatterns = [
    path('facturas/demo/', views.facturas_demo, name='facturas_demo'),
    path('demo/', views.ventas_demo, name='ventas_demo'),
    path('nueva/', views.nueva_venta, name='nueva_venta'),
]
