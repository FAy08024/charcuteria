
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator



class ActividadUsuario(models.Model):

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='acciones_realizadas'
    )

    usuario_objetivo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='acciones_recibidas'
    )

    accion = models.CharField(max_length=50)
    detalle = models.CharField(max_length=220)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Actividad de usuario'
        verbose_name_plural = 'Actividades de usuarios'

    def __str__(self):
        return self.detalle

class PerfilUsuario(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_usuario'
    )

    foto = models.ImageField(
        upload_to='usuarios/',
        blank=True,
        null=True
    )

    posicion_x = models.PositiveSmallIntegerField(
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    posicion_y = models.PositiveSmallIntegerField(
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    def __str__(self):
        return 'Perfil de ' + self.usuario.username



class TurnoEmpleado(models.Model):

    empleado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='turnos_empleado'
    )

    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)

    cantidad_ventas = models.PositiveIntegerField(default=0)
    cantidad_abonos = models.PositiveIntegerField(default=0)

    total_ventas = models.PositiveBigIntegerField(default=0)
    total_abonos = models.PositiveBigIntegerField(default=0)
    total_recaudado = models.PositiveBigIntegerField(default=0)

    revisado_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ['-inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['empleado'],
                condition=models.Q(fin__isnull=True),
                name='un_turno_abierto_por_empleado'
            )
        ]

    @property
    def abierto(self):
        return self.fin is None

    def __str__(self):
        return f'Turno {self.pk} - {self.empleado.username}'
