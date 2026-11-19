from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'cliente_nombre',
        'tipo',
        'estado',
        'total',
        'fecha',
    )

    list_filter = ('tipo', 'estado')
    search_fields = (
        'cliente_nombre',
        'cliente_codigo',
    )

    inlines = [DetalleVentaInline]