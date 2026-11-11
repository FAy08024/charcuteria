
from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'documento',
        'tipo',
        'estado',
        'fecha_registro',
    )

    search_fields = (
        'nombre',
        'documento',
    )

    list_filter = (
        'tipo',
        'estado',
    )

    readonly_fields = (
        'fecha_registro',
    )
