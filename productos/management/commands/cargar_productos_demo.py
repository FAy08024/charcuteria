
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from productos.models import Producto


PRODUCTOS_INICIALES = [
    {
        'codigo': 'PRO-001',
        'nombre': 'Jamón especial',
        'categoria': 'Jamones',
        'descripcion': (
            'Jamón seleccionado de excelente calidad, '
            'ideal para compartir en familia.'
        ),
        'precio_venta': Decimal('35000.00'),
        'descuento': 0,
        'imagen_archivo': 'jamon.png',
    },
    {
        'codigo': 'PRO-002',
        'nombre': 'Queso fresco',
        'categoria': 'Quesos',
        'descripcion': (
            'Queso fresco ideal para acompañar '
            'desayunos, mercados y preparaciones.'
        ),
        'precio_venta': Decimal('24000.00'),
        'descuento': 0,
        'imagen_archivo': None,
    },
    {
        'codigo': 'PRO-003',
        'nombre': 'Chorizo artesanal',
        'categoria': 'Chorizos',
        'descripcion': (
            'Chorizo de sabor tradicional, '
            'perfecto para asados y reuniones.'
        ),
        'precio_venta': Decimal('29000.00'),
        'descuento': 10,
        'imagen_archivo': 'chorizo.png',
    },
]


class Command(BaseCommand):
    help = 'Importar productos de demostración sin duplicarlos.'

    def handle(self, *args, **options):

        for datos in PRODUCTOS_INICIALES:
            codigo = datos['codigo']
            nombre = datos['nombre']

            if Producto.objects.filter(
                codigo__iexact=codigo
            ).exists():
                self.stdout.write(
                    f'Omitido: el código {codigo} ya existe.'
                )
                continue

            if Producto.objects.filter(
                nombre__iexact=nombre
            ).exists():
                self.stdout.write(
                    f'Omitido: el nombre {nombre} ya existe.'
                )
                continue

            producto = Producto.objects.create(
                codigo=codigo,
                nombre=nombre,
                categoria=datos['categoria'],
                descripcion=datos['descripcion'],
                precio_venta=datos['precio_venta'],
                descuento=datos['descuento'],
                unidad_medida='unidad',
                existencias=Decimal('0'),
                stock_minimo=Decimal('0'),
                activo=True,
            )

            nombre_imagen = datos['imagen_archivo']

            if nombre_imagen:
                ruta = (
                    Path(settings.BASE_DIR)
                    / 'static'
                    / 'img'
                    / nombre_imagen
                )

                if ruta.is_file():
                    with ruta.open('rb') as archivo:
                        producto.imagen.save(
                            nombre_imagen,
                            File(archivo),
                            save=True
                        )
                else:
                    self.stdout.write(
                        f'Imagen no encontrada: {ruta}'
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Creado: {codigo} - {nombre}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('Importación finalizada.')
        )
