
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# ==========================================
# ABONOS REGISTRADOS POR LOS EMPLEADOS
# ==========================================

class Abono(models.Model):

    METODOS = [
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
        ('Tarjeta', 'Tarjeta'),
    ]

    cuenta_numero = models.CharField(
        max_length=30,
        db_index=True
    )

    monto = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)]
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS
    )

    empleado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='abonos_registrados'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Abono'
        verbose_name_plural = 'Abonos'

    def __str__(self):
        return f'{self.cuenta_numero} - ${self.monto}'
