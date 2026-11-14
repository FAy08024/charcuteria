
from decimal import Decimal
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from clientes.views import CLIENTES_DEMO

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect
from django.utils import timezone

from ventas.models import Venta
from .models import Abono


# CUENTAS FICTICIAS
CUENTAS_DEMO = [
    {
        'cliente_id': 1,
        'numero': 'CRE-001',
        'capital': 400000,
        'tasa': '2.0',
        'abonos': 150000,
        'meses_transcurridos': 3,
        'plazo_meses': 6,
        'inicio': '12/08/2026',
        'vencimiento': '12/02/2027',
    },
    {
        'cliente_id': 3,
        'numero': 'CRE-002',
        'capital': 600000,
        'tasa': '1.5',
        'abonos': 100000,
        'meses_transcurridos': 2,
        'plazo_meses': 6,
        'inicio': '12/09/2026',
        'vencimiento': '12/03/2027',
    },
    {
        'cliente_id': 5,
        'numero': 'CRE-003',
        'capital': 280000,
        'tasa': '1.0',
        'abonos': 120000,
        'meses_transcurridos': 5,
        'plazo_meses': 6,
        'inicio': '12/06/2026',
        'vencimiento': '12/12/2026',
    },
]


def formato_pesos(valor):
    return '$' + format(valor, ',').replace(',', '.')



def obtener_cuentas_demo():

    clientes_por_id = {
        c['id']: c for c in CLIENTES_DEMO
    }

    clientes_por_codigo = {
        c['codigo']: c for c in CLIENTES_DEMO
    }

    # SUMAR LOS ABONOS GUARDADOS EN SQLITE
    abonos_por_cuenta = {
        fila['cuenta_numero']: fila['abonado']
        for fila in Abono.objects.values(
            'cuenta_numero'
        ).annotate(
            abonado=Sum('monto')
        )
    }

    cuentas = []

    # ======================================
    # CUENTAS FICTICIAS EXISTENTES
    # ======================================

    for cuenta in CUENTAS_DEMO:

        datos = cuenta.copy()

        datos['cliente'] = clientes_por_id[
            cuenta['cliente_id']
        ]

        capital = Decimal(cuenta['capital'])
        tasa = Decimal(cuenta['tasa']) / Decimal('100')

        interes = int(
            capital * tasa * cuenta['meses_transcurridos']
        )

        total = cuenta['capital'] + interes

        # ABONOS ANTERIORES + ABONOS NUEVOS
        abonos = (
            cuenta['abonos'] +
            abonos_por_cuenta.get(cuenta['numero'], 0)
        )

        saldo = max(total - abonos, 0)

        datos['interes'] = interes
        datos['total'] = total
        datos['abonos'] = abonos
        datos['saldo'] = saldo

        datos['estado'] = (
            'Pagada' if saldo == 0 else 'Pendiente'
        )

        datos['venta_id'] = None

        datos['meses_restantes'] = max(
            cuenta['plazo_meses'] -
            cuenta['meses_transcurridos'],
            0
        )

        datos['porcentaje'] = min(
            int(
                cuenta['meses_transcurridos']
                / cuenta['plazo_meses'] * 100
            ),
            100
        )

        datos['capital_formato'] = formato_pesos(
            cuenta['capital']
        )

        datos['interes_formato'] = formato_pesos(interes)
        datos['total_formato'] = formato_pesos(total)
        datos['abonos_formato'] = formato_pesos(abonos)
        datos['saldo_formato'] = formato_pesos(saldo)

        datos['meses'] = [
            {
                'numero': i,
                'transcurrido': (
                    i <= cuenta['meses_transcurridos']
                )
            }
            for i in range(
                1, cuenta['plazo_meses'] + 1
            )
        ]

        cuentas.append(datos)

    # ======================================
    # NUEVAS VENTAS A CRÉDITO
    # ======================================

    ventas_credito = Venta.objects.filter(
        tipo='Crédito'
    ).order_by('-fecha')

    for venta in ventas_credito:

        cliente = clientes_por_codigo.get(
            venta.cliente_codigo,
            {
                'id': None,
                'codigo': venta.cliente_codigo,
                'nombre': venta.cliente_nombre,
            }
        )

        abonos = abonos_por_cuenta.get(
            venta.numero, 0
        )

        saldo = max(
            venta.total - abonos, 0
        )

        fecha = timezone.localtime(venta.fecha)

        cuentas.append({
            'cliente_id': cliente['id'],
            'cliente': cliente,
            'numero': venta.numero,
            'capital': venta.total,
            'tasa': '0',
            'abonos': abonos,
            'meses_transcurridos': 0,
            'plazo_meses': 0,
            'inicio': fecha.strftime('%d/%m/%Y'),
            'vencimiento': 'Sin fecha definida',
            'interes': 0,
            'total': venta.total,
            'saldo': saldo,
            'estado': (
                'Pagada' if saldo == 0 else 'Pendiente'
            ),
            'venta_id': venta.pk,
            'meses_restantes': 0,
            'porcentaje': 0,
            'meses': [],
            'capital_formato': formato_pesos(venta.total),
            'interes_formato': formato_pesos(0),
            'total_formato': formato_pesos(venta.total),
            'abonos_formato': formato_pesos(abonos),
            'saldo_formato': formato_pesos(saldo),
        })

    return cuentas

# ==========================================
# AGRUPAR TODAS LAS DEUDAS POR CLIENTE
# ==========================================

def obtener_cuentas_agrupadas():

    grupos = {}

    # INCLUIR LOS 6 CLIENTES REGISTRADOS
    for cliente in CLIENTES_DEMO:

        grupos[cliente['id']] = {
            'cliente_id': cliente['id'],
            'cliente': cliente,
            'numero': 'Sin créditos',
            'capital': 0,
            'interes': 0,
            'total': 0,
            'abonos': 0,
            'saldo': 0,
            'tasa': '0',
            'estado': 'Sin deuda',
            'meses_transcurridos': 0,
            'plazo_meses': 0,
            'meses_restantes': 0,
            'porcentaje': 0,
            'inicio': 'Sin fecha',
            'vencimiento': 'Sin fecha definida',
            'meses': [],
            'creditos': [],
            'cantidad_creditos': 0,
            'creditos_pendientes': 0,
        }

    # AGRUPAR LOS CRÉDITOS Y ABONOS EXISTENTES
    for cuenta in obtener_cuentas_demo():

        grupo = grupos.get(cuenta['cliente_id'])

        if grupo is None:
            continue

        grupo['creditos'].append(cuenta)

        for campo in [
            'capital',
            'interes',
            'total',
            'abonos',
            'saldo'
        ]:
            grupo[campo] += cuenta[campo]

    # PREPARAR EL RESUMEN DE CADA CLIENTE
    for grupo in grupos.values():

        creditos = grupo['creditos']

        grupo['cantidad_creditos'] = len(creditos)

        grupo['creditos_pendientes'] = sum(
            1 for c in creditos if c['saldo'] > 0
        )

        if grupo['saldo'] > 0:
            grupo['estado'] = 'Pendiente'
        elif creditos:
            grupo['estado'] = 'Pagada'

        if len(creditos) == 1:

            cuenta = creditos[0]

            for campo in [
                'numero',
                'tasa',
                'meses_transcurridos',
                'plazo_meses',
                'meses_restantes',
                'porcentaje',
                'inicio',
                'vencimiento',
                'meses'
            ]:
                grupo[campo] = cuenta[campo]

        elif len(creditos) > 1:

            grupo['numero'] = (
                str(len(creditos)) + ' créditos'
            )

            grupo['inicio'] = 'Varias fechas'
            grupo['vencimiento'] = 'Varios vencimientos'

        # FORMATO DE DINERO
        for campo in [
            'capital',
            'interes',
            'total',
            'abonos',
            'saldo'
        ]:
            grupo[campo + '_formato'] = formato_pesos(
                grupo[campo]
            )

    return list(grupos.values())



def validar_acceso_cuentas(usuario):

    permitido = (
        usuario.is_superuser or
        usuario.groups.filter(
            name__in=['Administrador', 'Trabajador']
        ).exists()
    )

    if not permitido:
        raise PermissionDenied(
            'No tienes permiso para consultar cuentas.'
        )



@login_required(login_url='login')
def cuentas_demo(request):

    validar_acceso_cuentas(request.user)

    cuentas = obtener_cuentas_agrupadas()

    return render(
        request,
        'cuentas/lista_demo.html',
        {
            'cuentas': cuentas
        }
    )



@login_required(login_url='login')
def detalle_cuenta_demo(request, cliente_id):

    validar_acceso_cuentas(request.user)

    cuenta = next(
        (
            c for c in obtener_cuentas_agrupadas()
            if c['cliente_id'] == cliente_id
        ),
        None
    )

    if cuenta is None:
        raise Http404('Cliente no encontrado.')

    return render(
        request,
        'cuentas/detalle_demo.html',
        {
            'cuenta': cuenta,
            'creditos': cuenta['creditos']
        }
    )


@login_required(login_url='login')
def registrar_abono(request):

    validar_acceso_cuentas(request.user)

    error = None

    if request.method == 'POST':

        numero = request.POST.get(
            'cuenta_numero', ''
        ).strip()

        monto_texto = request.POST.get(
            'monto', ''
        ).strip()

        metodo = request.POST.get(
            'metodo_pago', ''
        ).strip()

        if metodo not in [
            'Efectivo',
            'Transferencia',
            'Tarjeta'
        ]:

            error = 'Selecciona un método de pago válido.'

        elif (
            not monto_texto.isdecimal() or
            int(monto_texto) <= 0
        ):

            error = 'Ingresa un monto mayor que cero.'

        else:

            monto = int(monto_texto)

            with transaction.atomic():

                # OBTENER SALDO ACTUALIZADO
                cuenta = next(
                    (
                        c for c in obtener_cuentas_demo()
                        if c['numero'] == numero
                    ),
                    None
                )

                if cuenta is None:

                    error = 'La cuenta no existe.'

                elif cuenta['saldo'] == 0:

                    error = 'Esta cuenta ya está pagada.'

                elif monto > cuenta['saldo']:

                    error = (
                        'El abono no puede superar '
                        'la deuda pendiente.'
                    )

                else:

                    # GUARDAR ABONO
                    Abono.objects.create(
                        cuenta_numero=numero,
                        monto=monto,
                        metodo_pago=metodo,
                        empleado=request.user
                    )

                    # ACTUALIZAR VENTA A CRÉDITO
                    if cuenta['venta_id'] is not None:

                        venta = Venta.objects.get(
                            pk=cuenta['venta_id']
                        )

                        venta.estado = (
                            'Pagada'
                            if monto == cuenta['saldo']
                            else 'Pendiente'
                        )

                        venta.save(
                            update_fields=['estado']
                        )

                    messages.success(
                        request,
                        f'Abono de {formato_pesos(monto)} '
                        f'registrado en {numero}.'
                    )

                    return redirect('registrar_abono')

    
    cuentas_pendientes = [
        cuenta
        for cuenta in obtener_cuentas_demo()
        if cuenta['saldo'] > 0
    ]

    # AGRUPAR LAS DEUDAS POR CLIENTE
    clientes_con_deuda = []

    for cliente in CLIENTES_DEMO:

        creditos = [
            cuenta
            for cuenta in cuentas_pendientes
            if cuenta['cliente_id'] == cliente['id']
        ]

        if creditos:

            saldo_total = sum(
                cuenta['saldo']
                for cuenta in creditos
            )

            clientes_con_deuda.append({
                'id': cliente['id'],
                'nombre': cliente['nombre'],
                'codigo': cliente['codigo'],
                'saldo': saldo_total,
                'saldo_formato': formato_pesos(saldo_total),
                'cantidad_creditos': len(creditos)
            })

    ultimos_abonos = Abono.objects.select_related(
        'empleado'
    )[:8]


    return render(
        request,
        'cuentas/registrar_abono.html',
        {
            'cuentas': cuentas_pendientes,
            'clientes_con_deuda': clientes_con_deuda,
            'ultimos_abonos': ultimos_abonos,
            'error': error,
        }
    )
