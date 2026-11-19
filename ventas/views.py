
import json
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect
from django.utils import timezone

from productos.models import Producto
from clientes.models import Cliente

from clientes.models import Cliente

from productos.models import Producto
from usuarios.models import TurnoEmpleado
from .models import Venta, DetalleVenta


# ==========================================
# FUNCIONES GENERALES
# ==========================================

def formato_venta(valor):
    return '$' + format(int(valor), ',').replace(',', '.')


def usuario_autorizado(usuario):
    return (
        usuario.is_active and
        (
            usuario.is_superuser or
            usuario.groups.filter(
                name__in=['Administrador', 'Trabajador']
            ).exists()
        )
    )


def usuario_administrador(usuario):
    return (
        usuario.is_active and
        (
            usuario.is_superuser or
            usuario.groups.filter(
                name='Administrador'
            ).exists()
        )
    )


# ==========================================
# FACTURAS FICTICIAS
# ==========================================

FACTURAS_DEMO = [
    {
        'numero': 'FAC-001',
        'cliente_id': 1,
        'hora': '08:35',
        'tipo': 'Crédito',
        'estado': 'Pendiente',
        'total': '$125.000',
        'productos': [
            {'nombre': 'Jamón', 'cantidad': 2},
            {'nombre': 'Chorizo', 'cantidad': 1},
            {'nombre': 'Queso', 'cantidad': 1},
        ]
    },
    {
        'numero': 'FAC-002',
        'cliente_id': 2,
        'hora': '09:12',
        'tipo': 'Contado',
        'estado': 'Pagada',
        'total': '$58.000',
        'productos': [
            {'nombre': 'Chorizo', 'cantidad': 2},
            {'nombre': 'Jamón', 'cantidad': 1},
        ]
    },
    {
        'numero': 'FAC-003',
        'cliente_id': 3,
        'hora': '10:04',
        'tipo': 'Crédito',
        'estado': 'Pendiente',
        'total': '$195.000',
        'productos': [
            {'nombre': 'Mercado familiar', 'cantidad': 2},
        ]
    },
    {
        'numero': 'FAC-004',
        'cliente_id': 4,
        'hora': '11:30',
        'tipo': 'Contado',
        'estado': 'Pagada',
        'total': '$42.000',
        'productos': [
            {'nombre': 'Jamón', 'cantidad': 2},
        ]
    },
    {
        'numero': 'FAC-005',
        'cliente_id': 6,
        'hora': '13:20',
        'tipo': 'Contado',
        'estado': 'Pagada',
        'total': '$61.000',
        'productos': [
            {'nombre': 'Combo especial', 'cantidad': 1},
        ]
    },
    {
        'numero': 'FAC-006',
        'cliente_id': 5,
        'hora': '14:05',
        'tipo': 'Crédito',
        'estado': 'Pendiente',
        'total': '$174.000',
        'productos': [
            {'nombre': 'Combo familiar', 'cantidad': 1},
            {'nombre': 'Embutidos', 'cantidad': 2},
        ]
    },
]


# ==========================================
# VISTA DE FACTURAS
# ==========================================


@login_required(login_url='login')
def facturas_demo(request):

    if not usuario_autorizado(request.user):
        raise PermissionDenied(
            'No tienes permiso para consultar facturas.'
        )

    clientes = Cliente.objects.all().order_by('nombre')

    ventas = Venta.objects.filter(
        fecha__date=timezone.localdate()
    ).prefetch_related(
        'detalles'
    ).order_by('-fecha')

    clientes_por_documento = {
        cliente.documento: cliente.pk
        for cliente in clientes
    }

    facturas = []

    for venta in ventas:

        detalles = [
            {
                'nombre': detalle.producto_nombre,
                'cantidad': detalle.cantidad,
            }
            for detalle in venta.detalles.all()
        ]

        facturas.append({
            'cliente_id': clientes_por_documento.get(venta.cliente_codigo, ''),
            'numero': venta.numero,
            'cliente': venta.cliente_nombre,
            'hora': timezone.localtime(
                venta.fecha
            ).strftime('%H:%M'),
            'tipo': venta.tipo,
            'estado': venta.estado,
            'total': formato_venta(venta.total),
            'productos': detalles,
        })

    return render(
        request,
        'ventas/facturas_demo.html',
        {
            'clientes': clientes,
            'facturas': facturas,
            'fecha_hoy': timezone.localdate(),
        }
    )



# ==========================================
# CREAR VENTAS FICTICIAS
# ==========================================

def crear_venta(numero, dias, hora, cliente, codigo,
                tipo, pago, estado, productos):

    fecha = timezone.localdate() - timedelta(days=dias)

    detalles = []
    total = 0

    for nombre, cantidad, precio in productos:

        importe = cantidad * precio
        total += importe

        detalles.append({
            'nombre': nombre,
            'cantidad': cantidad,
            'precio': precio,
            'precio_formato': formato_venta(precio),
            'importe_formato': formato_venta(importe),
        })

    return {
        'numero': numero,
        'cliente': cliente,
        'codigo': codigo,
        'fecha_iso': fecha.isoformat(),
        'fecha_texto': fecha.strftime('%d/%m/%Y'),
        'hora': hora,
        'tipo': tipo,
        'pago': pago,
        'estado': estado,
        'productos': detalles,
        'total': total,
        'total_formato': formato_venta(total),
    }


# ==========================================
# HISTORIAL DE VENTAS FICTICIAS
# ==========================================

def obtener_ventas_ficticias():

    return [
        crear_venta(
            'VEN-012', 0, '16:30',
            'Lara Greyrat', 'CLI-001',
            'Crédito', 'Crédito de mercado', 'Pendiente',
            [
                ('Jamón especial', 2, 35000),
                ('Queso fresco', 1, 24000),
                ('Chorizo artesanal', 1, 31000),
            ]
        ),

        crear_venta(
            'VEN-011', 0, '13:18',
            'Cliente ocasional', 'Sin registro',
            'Contado', 'Efectivo', 'Pagada',
            [
                ('Combo especial', 1, 84000),
            ]
        ),

        crear_venta(
            'VEN-010', 0, '11:20',
            'Camila Torres', 'CLI-003',
            'Crédito', 'Crédito de mercado', 'Pendiente',
            [
                ('Mercado familiar', 2, 110000),
            ]
        ),

        crear_venta(
            'VEN-009', 1, '15:35',
            'Daniel Rojas', 'CLI-002',
            'Contado', 'Transferencia', 'Pagada',
            [
                ('Chorizo artesanal', 2, 29000),
            ]
        ),

        crear_venta(
            'VEN-008', 3, '14:10',
            'Cliente ocasional', 'Sin registro',
            'Contado', 'Efectivo', 'Pagada',
            [
                ('Jamón especial', 2, 35000),
                ('Queso fresco', 1, 24000),
            ]
        ),

        crear_venta(
            'VEN-007', 6, '09:45',
            'Andrés Peña', 'CLI-004',
            'Contado', 'Efectivo', 'Pagada',
            [
                ('Embutidos surtidos', 1, 42000),
            ]
        ),

        crear_venta(
            'VEN-006', 10, '16:05',
            'Juliana Pardo', 'CLI-005',
            'Crédito', 'Crédito de mercado', 'Pendiente',
            [
                ('Mercado familiar', 1, 110000),
                ('Embutidos especiales', 2, 32000),
            ]
        ),

        crear_venta(
            'VEN-005', 18, '12:50',
            'Cliente ocasional', 'Sin registro',
            'Contado', 'Tarjeta', 'Pagada',
            [
                ('Combo especial', 1, 84000),
                ('Chorizo artesanal', 1, 29000),
            ]
        ),

        crear_venta(
            'VEN-004', 28, '10:15',
            'Nicolás Cárdenas', 'CLI-006',
            'Contado', 'Efectivo', 'Pagada',
            [
                ('Chorizo artesanal', 2, 31000),
            ]
        ),

        crear_venta(
            'VEN-003', 65, '17:10',
            'Laura Pardo', 'Sin registro',
            'Contado', 'Transferencia', 'Pagada',
            [
                ('Mercado familiar', 1, 110000),
            ]
        ),

        crear_venta(
            'VEN-002', 180, '09:30',
            'Cliente ocasional', 'Sin registro',
            'Contado', 'Efectivo', 'Pagada',
            [
                ('Tabla de embutidos', 1, 45000),
            ]
        ),

        crear_venta(
            'VEN-001', 370, '15:40',
            'Lara Greyrat', 'CLI-001',
            'Contado', 'Transferencia', 'Pagada',
            [
                ('Combo especial', 1, 84000),
            ]
        ),
    ]


# ==========================================
# CONECTAR VENTAS NUEVAS CON HISTORIAL
# ==========================================

def obtener_ventas_demo():

    ventas = []

    ventas_guardadas = Venta.objects.prefetch_related(
        'detalles'
    ).order_by('-fecha')

    for venta in ventas_guardadas:

        fecha = timezone.localtime(venta.fecha)

        productos = [
            {
                'nombre': detalle.producto_nombre,
                'cantidad': detalle.cantidad,
                'precio': detalle.precio_unitario,
                'precio_formato': formato_venta(
                    detalle.precio_unitario
                ),
                'importe_formato': formato_venta(
                    detalle.importe
                ),
            }
            for detalle in venta.detalles.all()
        ]

        ventas.append({
            'numero': venta.numero,
            'cliente': venta.cliente_nombre,
            'codigo': venta.cliente_codigo,
            'fecha_iso': fecha.date().isoformat(),
            'fecha_texto': fecha.strftime('%d/%m/%Y'),
            'hora': fecha.strftime('%H:%M'),
            'tipo': venta.tipo,
            'pago': venta.metodo_pago,
            'estado': venta.estado,
            'productos': productos,
            'total': venta.total,
            'total_formato': formato_venta(venta.total),
        })

    return ventas


# ==========================================
# HISTORIAL DE VENTAS DEL ADMINISTRADOR
# ==========================================

@login_required(login_url='login')
def ventas_demo(request):

    if not usuario_administrador(request.user):
        raise PermissionDenied(
            'Solo el administrador puede consultar esta sección.'
        )

    ventas = obtener_ventas_demo()

    return render(request, 'ventas/ventas_demo.html', {
        'ventas': ventas,
        'fecha_hoy': timezone.localdate(),
    })


# ==========================================
# CATÁLOGO PARA NUEVA VENTA
# ==========================================


# ==========================================
# CATÁLOGO REAL PARA NUEVA VENTA
# ==========================================

def catalogo_para_venta():

    catalogo = []

    productos = Producto.objects.filter(
        activo=True
    ).order_by('nombre')

    iconos = {
        'Quesos': '🧀',
        'Jamones': '🥩',
        'Chorizos': '🌭',
    }

    for producto in productos:

        precio = producto.precio_venta
        descuento = Decimal(producto.descuento)

        if precio <= 0 or not 0 <= descuento <= 100:
            raise ValueError(
                'Precio o descuento inválido.'
            )

        precio_final = int(
            (
                precio * (Decimal('100') - descuento)
                / Decimal('100')
            ).quantize(
                Decimal('1'),
                rounding=ROUND_HALF_UP
            )
        )

        catalogo.append({
            'id': producto.pk,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'categoria': producto.categoria or 'Sin categoría',
            'imagen': (
                producto.imagen.url if producto.imagen else ''
            ),
            'icono': iconos.get(
                producto.categoria, '📦'
            ),
            'precio': precio_final,
            'descuento': int(descuento),
        })

    return catalogo



# ==========================================
# VALIDAR PRODUCTOS DEL CARRITO
# ==========================================

def validar_carrito(datos_json, catalogo):

    try:
        items = json.loads(datos_json)

    except (TypeError, json.JSONDecodeError):
        raise ValueError(
            'El carrito no es válido.'
        )

    if not isinstance(items, list) or not 1 <= len(items) <= 30:
        raise ValueError(
            'Selecciona entre 1 y 30 productos diferentes.'
        )

    productos_por_id = {
        producto['id']: producto
        for producto in catalogo
    }

    resultado = []
    total = 0
    vistos = set()

    for item in items:

        if not isinstance(item, dict):
            raise ValueError('Producto inválido.')

        producto_id = item.get('id')
        cantidad = item.get('cantidad')

        if (
            type(producto_id) is not int or
            type(cantidad) is not int
        ):
            raise ValueError(
                'Producto o cantidad inválidos.'
            )

        if producto_id not in productos_por_id:
            raise ValueError(
                'El producto no existe.'
            )

        if not 1 <= cantidad <= 100:
            raise ValueError(
                'La cantidad debe estar entre 1 y 100.'
            )

        if producto_id in vistos:
            raise ValueError(
                'Producto duplicado.'
            )

        vistos.add(producto_id)

        producto = productos_por_id[producto_id]

        importe = producto['precio'] * cantidad
        total += importe

        resultado.append({
            **producto,
            'cantidad': cantidad,
            'importe': importe,
        })

    if total <= 0:
        raise ValueError(
            'El total debe ser mayor que cero.'
        )

    return resultado, total


# ==========================================
# REGISTRAR NUEVA VENTA - EMPLEADO
# ==========================================

@login_required(login_url='login')
def nueva_venta(request):

    if not usuario_autorizado(request.user):
        raise PermissionDenied(
            'No tienes permiso para registrar ventas.'
        )

    # ==========================================
    # COMPROBAR TURNO DEL EMPLEADO
    # ==========================================

    if request.user.groups.filter(
        name='Trabajador'
    ).exists() and not usuario_administrador(request.user):

        turno_abierto = TurnoEmpleado.objects.filter(
            empleado=request.user,
            fin__isnull=True
        ).exists()

        if not turno_abierto:

            messages.warning(
                request,
                'Debes iniciar tu turno antes de registrar ventas.'
            )

            return redirect('panel_empleado')

    # ==========================================
    # CATÁLOGO Y FORMULARIO
    # ==========================================

    catalogo = catalogo_para_venta()
    error = None

    if request.method == 'POST':

        try:

            # VALIDAR LOS PRODUCTOS
            productos, total = validar_carrito(
                request.POST.get('items_json', ''),
                catalogo
            )

            # TIPO DE VENTA
            tipo = request.POST.get(
                'tipo', 'Contado'
            )

            if tipo not in ['Contado', 'Crédito']:
                raise ValueError(
                    'Tipo de venta inválido.'
                )

            # CLIENTE

            # CLIENTE REAL DE SQLITE
            cliente_id = request.POST.get(
                'cliente_id', ''
            ).strip()

            cliente_registrado = None

            if cliente_id:

                if not cliente_id.isdecimal():
                    raise ValueError(
                        'Identificador de cliente inválido.'
                    )

                cliente_registrado = Cliente.objects.filter(
                    pk=int(cliente_id)
                ).first()

                if cliente_registrado is None:
                    raise ValueError(
                        'El cliente seleccionado no existe.'
                    )

                if cliente_registrado.estado != 'ACTIVO':
                    raise ValueError(
                        'El cliente está bloqueado o inactivo.'
                    )

            # AUTORIZACIÓN DEL CRÉDITO
            if tipo == 'Crédito':

                if cliente_registrado is None:
                    raise ValueError(
                        'Selecciona un cliente registrado.'
                    )

                if cliente_registrado.tipo != 'MAYORISTA':
                    raise ValueError(
                        'El crédito es exclusivo '
                        'para clientes mayoristas.'
                    )

            # DATOS HISTÓRICOS
            if cliente_registrado:

                nombre = cliente_registrado.nombre
                codigo = cliente_registrado.codigo

            else:

                nombre = (
                    request.POST.get(
                        'cliente_ocasional', ''
                    ).strip()
                    or 'Cliente ocasional'
                )

                codigo = 'Sin registro'

            if len(nombre) > 120:
                raise ValueError(
                    'Nombre del cliente demasiado largo.'
                )



            # MÉTODO DE PAGO
            if tipo == 'Crédito':

                metodo = 'Crédito de mercado'
                estado = 'Pendiente'

            else:

                metodo = request.POST.get(
                    'metodo_pago', ''
                )

                if metodo not in [
                    'Efectivo',
                    'Transferencia',
                    'Tarjeta',
                ]:
                    raise ValueError(
                        'Método de pago inválido.'
                    )

                estado = 'Pagada'

            # ==========================================
            # GUARDAR VENTA EN SQLITE
            # ==========================================

            
            # DESCONTAR INVENTARIO UNA SOLA VEZ
            with transaction.atomic():

                # Descontar inventario
                for item in productos:
                    cantidad = Decimal(str(item['cantidad']))

                    actualizado = Producto.objects.filter(
                        pk=item['id'],
                        activo=True,
                        existencias__gte=cantidad
                    ).update(
                        existencias=F('existencias') - cantidad
                    )

                    if actualizado != 1:
                        raise ValueError(
                            f"Existencias insuficientes de {item['nombre']}."
                        )

                # Guardar la venta
                venta = Venta.objects.create(
                            cliente=cliente_registrado,
                            cliente_nombre=nombre,
                            cliente_codigo=codigo,
                            tipo=tipo,
                            metodo_pago=metodo,
                            estado=estado,
                            total=total,
                            empleado=request.user
                )

                # Guardar los productos vendidos
                detalles = [
                    DetalleVenta(
                        venta=venta,
                        producto_codigo=item['codigo'],
                        producto_nombre=item['nombre'],
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio'],
                        importe=item['importe']
                    )
                    for item in productos
                ]

                DetalleVenta.objects.bulk_create(detalles)

            messages.success(
                request,
                f'{venta.numero} registrada correctamente '
                f'por {formato_venta(total)}.'
            )

            return redirect('nueva_venta')

        except ValueError as error_venta:

            error = str(error_venta)

    return render(
    request,
    'ventas/nueva_venta.html',
    {
        'catalogo': catalogo,
        'clientes': Cliente.objects.all().order_by('nombre'),
        'error': error,
        'ventas_recientes': Venta.objects.all()[:5],
    }
)