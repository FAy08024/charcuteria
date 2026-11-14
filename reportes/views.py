
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from clientes.views import CLIENTES_DEMO

from ventas.models import Venta
from cuentas.models import Abono


# HISTORIAL FICTICIO
MOVIMIENTOS_DEMO = [
    {
        'cliente_id': 1,
        'tipo': 'venta',
        'numero': 'VEN-001',
        'fecha': '04/11/2026',
        'descripcion': 'Venta a crédito',
        'detalle': 'Jamón x2, Chorizo x1, Queso x1',
        'valor': 125000,
        'estado': 'Registrada',
    },
    {
        'cliente_id': 1,
        'tipo': 'factura',
        'numero': 'FAC-001',
        'fecha': '04/11/2026',
        'descripcion': 'Factura de la venta VEN-001',
        'detalle': 'Compra a crédito',
        'valor': 125000,
        'estado': 'Pendiente',
    },
    {
        'cliente_id': 1,
        'tipo': 'abono',
        'numero': 'ABO-001',
        'fecha': '07/11/2026',
        'descripcion': 'Abono a la factura FAC-001',
        'detalle': 'Pago parcial en efectivo',
        'valor': 45000,
        'estado': 'Recibido',
    },
    {
        'cliente_id': 2,
        'tipo': 'venta',
        'numero': 'VEN-002',
        'fecha': '06/11/2026',
        'descripcion': 'Venta de contado',
        'detalle': 'Chorizo x2, Jamón x1',
        'valor': 58000,
        'estado': 'Registrada',
    },
    {
        'cliente_id': 2,
        'tipo': 'factura',
        'numero': 'FAC-002',
        'fecha': '06/11/2026',
        'descripcion': 'Factura de la venta VEN-002',
        'detalle': 'Pago de contado',
        'valor': 58000,
        'estado': 'Pagada',
    },
    {
        'cliente_id': 3,
        'tipo': 'venta',
        'numero': 'VEN-003',
        'fecha': '09/11/2026',
        'descripcion': 'Venta a crédito',
        'detalle': 'Mercado familiar x2',
        'valor': 195000,
        'estado': 'Registrada',
    },
    {
        'cliente_id': 3,
        'tipo': 'factura',
        'numero': 'FAC-003',
        'fecha': '09/11/2026',
        'descripcion': 'Factura de la venta VEN-003',
        'detalle': 'Compra a crédito',
        'valor': 195000,
        'estado': 'Pendiente',
    },
    {
        'cliente_id': 3,
        'tipo': 'abono',
        'numero': 'ABO-002',
        'fecha': '10/11/2026',
        'descripcion': 'Abono a la factura FAC-003',
        'detalle': 'Pago parcial en efectivo',
        'valor': 75000,
        'estado': 'Recibido',
    },
    {
        'cliente_id': 4,
        'tipo': 'venta',
        'numero': 'VEN-004',
        'fecha': '10/11/2026',
        'descripcion': 'Venta de contado',
        'detalle': 'Jamón x2',
        'valor': 42000,
        'estado': 'Registrada',
    },
    {
        'cliente_id': 4,
        'tipo': 'factura',
        'numero': 'FAC-004',
        'fecha': '10/11/2026',
        'descripcion': 'Factura de la venta VEN-004',
        'detalle': 'Pago de contado',
        'valor': 42000,
        'estado': 'Pagada',
    },
    {
        'cliente_id': 5,
        'tipo': 'venta',
        'numero': 'VEN-005',
        'fecha': '11/11/2026',
        'descripcion': 'Venta histórica a crédito',
        'detalle': 'Combo familiar x1, Embutidos x2',
        'valor': 174000,
        'estado': 'Registrada',
    },
    {
        'cliente_id': 5,
        'tipo': 'factura',
        'numero': 'FAC-006',
        'fecha': '11/11/2026',
        'descripcion': 'Factura de la venta VEN-005',
        'detalle': 'Compra histórica a crédito',
        'valor': 174000,
        'estado': 'Pendiente',
    },
    {
        'cliente_id': 6,
        'tipo': 'venta',
        'numero': 'VEN-006',
        'fecha': '12/11/2026',
        'descripcion': 'Venta de contado',
        'detalle': 'Combo especial x1',
        'valor': 61000,
        'estado': 'Registrada',
    },
    {
        'cliente_id': 6,
        'tipo': 'factura',
        'numero': 'FAC-005',
        'fecha': '12/11/2026',
        'descripcion': 'Factura de la venta VEN-006',
        'detalle': 'Pago de contado',
        'valor': 61000,
        'estado': 'Pagada',
    },
]



# ==========================================
# HISTORIAL DE CLIENTES: DEMO + SQLITE
# ==========================================

@login_required(login_url='login')
def historial_demo(request):

    usuario = request.user

    autorizado = (
        usuario.is_active and
        (
            usuario.is_superuser or
            usuario.groups.filter(
                name__in=['Administrador', 'Trabajador']
            ).exists()
        )
    )

    if not autorizado:
        raise PermissionDenied(
            'No tienes permiso para consultar el historial.'
        )

    # CLIENTES QUE YA TENEMOS
    clientes = [
        cliente.copy()
        for cliente in CLIENTES_DEMO
    ]

    clientes_por_codigo = {
        cliente['codigo']: cliente['id']
        for cliente in CLIENTES_DEMO
    }

    # MOVIMIENTOS FICTICIOS EXISTENTES
    movimientos = [
        movimiento.copy()
        for movimiento in MOVIMIENTOS_DEMO
    ]

    movimientos_reales = []

    # ======================================
    # VENTAS REGISTRADAS POR LOS EMPLEADOS
    # ======================================

    ventas_guardadas = Venta.objects.select_related(
        'empleado'
    ).prefetch_related(
        'detalles'
    ).order_by('-fecha')

    for venta in ventas_guardadas:

        cliente_id = clientes_por_codigo.get(
            venta.cliente_codigo,
            0
        )

        # RESUMEN DE LOS PRODUCTOS COMPRADOS
        productos = []

        for detalle in venta.detalles.all():

            productos.append(
                f'{detalle.producto_nombre} '
                f'x{detalle.cantidad}'
            )

        resumen = ', '.join(productos)

        if not resumen:
            resumen = 'Sin productos detallados'

        # SI NO ESTÁ REGISTRADO, MOSTRAR SU NOMBRE
        if (
            cliente_id == 0 and
            venta.cliente_nombre != 'Cliente ocasional'
        ):

            resumen += (
                ' · Nombre indicado: '
                + venta.cliente_nombre
            )

        # EMPLEADO QUE REGISTRÓ LA VENTA
        if venta.empleado:

            nombre_empleado = venta.empleado.username

        else:

            nombre_empleado = 'No disponible'

        resumen += (
            ' · ' + venta.metodo_pago
            + ' · Registró: ' + nombre_empleado
        )

        fecha = timezone.localtime(venta.fecha)

        movimientos_reales.append({
            'cliente_id': cliente_id,
            'tipo': 'venta',
            'numero': venta.numero,
            'fecha': fecha.strftime('%d/%m/%Y %H:%M'),
            'descripcion': (
                'Venta a ' + venta.tipo.lower()
            ),
            'detalle': resumen,
            'valor': venta.total,
            'estado': venta.estado,
            'fecha_orden': venta.fecha,
        })

    # ======================================
    # ABONOS REGISTRADOS POR LOS EMPLEADOS
    # ======================================

    from cuentas.views import obtener_cuentas_demo

    cuentas_por_numero = {
        cuenta['numero']: cuenta
        for cuenta in obtener_cuentas_demo()
    }

    abonos_guardados = Abono.objects.select_related(
        'empleado'
    ).order_by('-fecha')

    for abono in abonos_guardados:

        cuenta = cuentas_por_numero.get(
            abono.cuenta_numero
        )

        if cuenta is None:
            # No asociar el pago al cliente equivocado.
            continue

        cliente_id = cuenta.get('cliente_id')

        if cliente_id is None:
            cliente_id = 0

        if abono.empleado:

            nombre_empleado = abono.empleado.username

        else:

            nombre_empleado = 'No disponible'

        fecha = timezone.localtime(abono.fecha)

        movimientos_reales.append({
            'cliente_id': cliente_id,
            'tipo': 'abono',
            'numero': f'ABO-R{abono.pk:03d}',
            'fecha': fecha.strftime('%d/%m/%Y %H:%M'),
            'descripcion': (
                'Abono a la cuenta '
                + abono.cuenta_numero
            ),
            'detalle': (
                'Pago en ' + abono.metodo_pago
                + ' · Registró: ' + nombre_empleado
            ),
            'valor': abono.monto,
            'estado': 'Recibido',
            'fecha_orden': abono.fecha,
        })

    # MOSTRAR PRIMERO LAS OPERACIONES RECIENTES
    movimientos_reales.sort(
        key=lambda m: m['fecha_orden'],
        reverse=True
    )

    for movimiento in movimientos_reales:
        movimiento.pop('fecha_orden', None)

    movimientos = movimientos_reales + movimientos

    # ======================================
    # AGREGAR CLIENTE OCASIONAL
    # ======================================

    hay_ocasionales = any(
        movimiento['cliente_id'] == 0
        for movimiento in movimientos
    )

    if hay_ocasionales:

        clientes.append({
            'id': 0,
            'codigo': 'SIN-REGISTRO',
            'nombre': 'Cliente ocasional',
            'iniciales': 'CO',
            'tipo': 'Sin registro',
            'estado': 'Activo',
            'fecha': 'Sin fecha de registro',
            'foto': '',
        })

    # ======================================
    # ACTUALIZAR CONTADORES POR CLIENTE
    # ======================================

    for cliente in clientes:

        movimientos_cliente = [
            movimiento
            for movimiento in movimientos
            if movimiento['cliente_id'] == cliente['id']
        ]

        cliente['cantidad_ventas'] = sum(
            1 for movimiento in movimientos_cliente
            if movimiento['tipo'] == 'venta'
        )

        cliente['cantidad_facturas'] = sum(
            1 for movimiento in movimientos_cliente
            if movimiento['tipo'] == 'factura'
        )

        cliente['cantidad_abonos'] = sum(
            1 for movimiento in movimientos_cliente
            if movimiento['tipo'] == 'abono'
        )

    # ======================================
    # FORMATO DE DINERO
    # ======================================

    for movimiento in movimientos:

        movimiento['valor_formato'] = (
            '$' + format(
                int(movimiento['valor']), ','
            ).replace(',', '.')
        )

    return render(
        request,
        'reportes/historial_demo.html',
        {
            'clientes': clientes,
            'cliente_inicial': (
                clientes[0] if clientes else None
            ),
            'movimientos': movimientos,
        }
    )


from datetime import date, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone


CAPITAL_INICIAL_REPORTES = 4000000


def generar_reporte_demo():

    # Reutilizamos las ventas de nuestro otro módulo
    from ventas.views import obtener_ventas_demo

    ventas = obtener_ventas_demo()
    hoy = timezone.localdate()
    eventos = {}

    def obtener_dia(fecha):

        clave = fecha.isoformat()

        if clave not in eventos:
            eventos[clave] = {
                'ventas': 0,
                'costos': 0,
                'gastos': 0,
                'perdidas': 0,
                'intereses': 0,
                'cantidad': 0,
                'credito': 0,
                'contado': 0,
            }

        return eventos[clave]

    # INGRESOS Y COSTOS DE LAS VENTAS
    for venta in ventas:

        fecha = date.fromisoformat(venta['fecha_iso'])
        dia = obtener_dia(fecha)

        total = int(venta['total'])

        # Suposiciones ficticias:
        # Costo de mercancía: 68%
        # Gastos operativos: 5%
        dia['ventas'] += total
        dia['costos'] += round(total * 0.68)
        dia['gastos'] += round(total * 0.05)
        dia['cantidad'] += 1

        if venta['tipo'] == 'Crédito':
            dia['credito'] += total
        else:
            dia['contado'] += total

    # INGRESOS FICTICIOS POR INTERESES COBRADOS
    # Son registros simulados, no cobros reales.
    intereses_demo = [
        (0, 4500),
        (3, 4000),
        (6, 3500),
    ]

    for dias, monto in intereses_demo:
        fecha = hoy - timedelta(days=dias)
        obtener_dia(fecha)['intereses'] += monto

    # PÉRDIDAS FICTICIAS POR MERMAS
    perdidas_demo = [
        (0, 9000),
        (6, 15000),
        (17, 27000),
        (75, 45000),
        (200, 13000),
    ]

    for dias, monto in perdidas_demo:
        fecha = hoy - timedelta(days=dias)
        obtener_dia(fecha)['perdidas'] += monto

    # CALCULAR LA EVOLUCIÓN DIARIA DEL CAPITAL
    fecha_inicial = min(
        date.fromisoformat(clave)
        for clave in eventos
    )

    # Un día inicial para ver el capital de partida
    fecha_inicial -= timedelta(days=1)

    capital = CAPITAL_INICIAL_REPORTES
    registros = []

    fecha = fecha_inicial

    while fecha <= hoy:

        clave = fecha.isoformat()

        datos = eventos.get(clave, {
            'ventas': 0,
            'costos': 0,
            'gastos': 0,
            'perdidas': 0,
            'intereses': 0,
            'cantidad': 0,
            'credito': 0,
            'contado': 0,
        })

        resultado = (
            datos['ventas']
            + datos['intereses']
            - datos['costos']
            - datos['gastos']
            - datos['perdidas']
        )

        capital += resultado

        registros.append({
            'fecha': clave,
            'fecha_texto': fecha.strftime('%d/%m/%Y'),
            **datos,
            'resultado': resultado,
            'capital': capital,
        })

        fecha += timedelta(days=1)

    return registros


@login_required(login_url='login')
def reporte_financiero_demo(request):

    usuario = request.user

    es_administrador = (
        usuario.is_superuser or
        usuario.groups.filter(
            name='Administrador'
        ).exists()
    )

    if not es_administrador:
        raise PermissionDenied(
            'Solo el administrador puede consultar reportes.'
        )

    return render(request, 'reportes/reporte_financiero_demo.html', {
        'registros': generar_reporte_demo(),
        'capital_inicial': CAPITAL_INICIAL_REPORTES,
        'fecha_hoy': timezone.localdate(),
    })

