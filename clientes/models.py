
from django.db import models


class Cliente(models.Model):

    TIPOS_CLIENTE = [
        ('MINORISTA', 'Minorista'),
        ('MAYORISTA', 'Mayorista'),
    ]

    ESTADOS_CLIENTE = [
        ('ACTIVO', 'Activo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('INACTIVO', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=150)

    documento = models.CharField(
        max_length=20,
        unique=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    direccion = models.CharField(
        max_length=200,
        blank=True
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS_CLIENTE,
        default='MINORISTA'
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS_CLIENTE,
        default='ACTIVO'
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.documento}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
