
from django.conf import settings
from django.db import models


class Venta(models.Model):
    TIPOS = [
        ('Contado', 'Contado'),
        ('Crédito', 'Crédito'),
    ]
    ESTADOS = [
        ('Pagada', 'Pagada'),
        ('Pendiente', 'Pendiente'),
    ]

    cliente_nombre = models.CharField(max_length=120, default='Cliente ocasional')
    cliente_codigo = models.CharField(max_length=30, default='Sin registro')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    metodo_pago = models.CharField(max_length=30)
    estado = models.CharField(max_length=12, choices=ESTADOS)
    total = models.PositiveBigIntegerField()
    empleado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ventas_registradas'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    @property
    def numero(self):
        return f'VEN-{self.pk + 12:03d}' if self.pk else 'VEN-NUEVA'

    def __str__(self):
        return f'{self.numero} - {self.cliente_nombre}'


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto_codigo = models.CharField(max_length=30)
    producto_nombre = models.CharField(max_length=150)
    cantidad = models.PositiveSmallIntegerField()
    precio_unitario = models.PositiveBigIntegerField()
    importe = models.PositiveBigIntegerField()

    def __str__(self):
        return f'{self.cantidad} x {self.producto_nombre}'
