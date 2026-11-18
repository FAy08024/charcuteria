
from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = (
        'codigo',
        'nombre',
        'categoria',
        'precio_venta',
        'existencias',
        'unidad_medida',
        'activo',
    )

    search_fields = (
        'codigo',
        'nombre',
    )

    list_filter = (
        'categoria',
        'activo',
        'unidad_medida',
    )
