
from decimal import Decimal

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

class Producto(models.Model):
    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    categoria = models.CharField(
        max_length=100,
        blank=True
    )

    descripcion = models.TextField(
        blank=True
    )

    unidad_medida = models.CharField(
        max_length=20,
        default='unidad'
    )

    precio_venta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'))
        ]
    )
    descuento = models.PositiveSmallIntegerField(
    default=0,
    validators=[MaxValueValidator(100)]
    )

    existencias = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[
            MinValueValidator(Decimal('0'))
        ]
    )

    stock_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[
            MinValueValidator(Decimal('0'))
        ]
    )

    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True
    )

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Combo(models.Model):
    nombre = models.CharField(max_length=100)

    producto_uno = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='combos_producto_uno'
    )

    producto_dos = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='combos_producto_dos'
    )

    descuento = models.PositiveSmallIntegerField(
        default=20,
        editable=False
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Combo'
        verbose_name_plural = 'Combos'

    @property
    def codigo(self):
        if self.pk is None:
            return ''
        return f'COM-{self.pk:03d}'

    @property
    def precio_base(self):
        return (
            self.producto_uno.precio_venta +
            self.producto_dos.precio_venta
        )

    @property
    def precio_final(self):
        return (
            self.precio_base *
            (100 - self.descuento) / 100
        )

    def clean(self):
        if (
            self.producto_uno_id is not None
            and self.producto_uno_id == self.producto_dos_id
        ):
            raise ValidationError(
                'El combo debe tener dos productos diferentes.'
            )

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
