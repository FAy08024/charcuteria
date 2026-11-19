
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

    @property
    def codigo(self):
        if self.pk is None:
            return 'CLI-NUEVO'
        return f'CLI-{self.pk:03d}'

    @property
    def iniciales(self):
        partes = self.nombre.strip().split()
        return ''.join(
            palabra[0] for palabra in partes[:2]
        ).upper() or 'CL'
    foto = models.ImageField(
        upload_to='clientes/',
        blank=True,
        verbose_name='Foto del cliente'
    )   
    @property
    def fecha(self):
        from django.utils import timezone
        return timezone.localtime(
            self.fecha_registro
        ).strftime('%d/%m/%Y')
