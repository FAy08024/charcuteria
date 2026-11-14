
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# AJUSTES APROBADOS SOBRE EL INVENTARIO DEMO
class AjusteExistencia(models.Model):

    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    diferencia = models.IntegerField(default=0)

    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.codigo}: {self.diferencia:+d}'


# REPORTES ENVIADOS POR EMPLEADOS
class IncidenciaInventario(models.Model):

    TIPOS = [
        ('danado', 'Producto dañado'),
        ('diferencia', 'Diferencia de existencias'),
        ('reposicion', 'Solicitud de reposición'),
        ('otro', 'Otro problema'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('revision', 'En revisión'),
        ('resuelta', 'Resuelta'),
        ('descartada', 'Descartada'),
    ]

    ACCIONES = [
        ('', 'Sin decisión'),
        ('baja', 'Retirar unidades'),
        ('reemplazar', 'Sustituir por mercancía sana'),
        ('descartar', 'Descartar reporte'),
    ]

    producto_codigo = models.CharField(max_length=30)
    producto_nombre = models.CharField(max_length=150)

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    descripcion = models.TextField(max_length=700)

    foto = models.ImageField(
        upload_to='incidencias/',
        blank=True,
        null=True
    )

    empleado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incidencias_reportadas'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='pendiente'
    )

    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        blank=True,
        default=''
    )

    codigo_reemplazo = models.CharField(
        max_length=30,
        blank=True
    )

    respuesta = models.TextField(blank=True)

    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_resueltas'
    )

    fecha_resolucion = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.producto_codigo} - {self.get_estado_display()}'
