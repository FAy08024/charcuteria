from django.contrib import admin
from .models import Abono


@admin.register(Abono)
class AbonoAdmin(admin.ModelAdmin):
    list_display = (
        'cuenta_numero',
        'monto',
        'metodo_pago',
        'empleado',
        'fecha',
    )

    search_fields = ('cuenta_numero',)