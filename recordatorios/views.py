
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone

from cuentas.views import obtener_cuentas_demo


# ==========================================
# RECORDATORIOS DE CUENTAS PENDIENTES
# ==========================================

DIAS_PROXIMOS = 30


def formato_pesos_recordatorio(valor):
    return '$' + format(int(valor), ',').replace(',', '.')


def obtener_recordatorios():

    hoy = timezone.localdate()
    cuentas = obtener_cuentas_demo()

    recordatorios = []

    for cuenta in cuentas:

        saldo = int(cuenta['saldo'])

        # NO MOSTRAR DEUDAS PAGADAS
        if saldo <= 0:
            continue

        fecha_texto = cuenta.get('vencimiento', '')
        fecha_vencimiento = None

        # CONVERTIR LA FECHA
        try:
            fecha_vencimiento = datetime.strptime(
                fecha_texto,
                '%d/%m/%Y'
            ).date()

        except (ValueError, TypeError):
            pass

        # CLASIFICAR LA CUENTA
        if fecha_vencimiento is None:

            estado = 'sin_fecha'
            estado_texto = 'Sin fecha definida'
            descripcion = 'Pendiente de seguimiento'
            icono = '📅'
            prioridad = 2
            dias = 999999

        else:

            dias = (
                fecha_vencimiento - hoy
            ).days

            if dias < 0:

                estado = 'vencida'
                estado_texto = 'Vencida'
                descripcion = (
                    f'Venció hace {abs(dias)} '
                    f'{"día" if abs(dias) == 1 else "días"}'
                )
                icono = '🚨'
                prioridad = 0

            elif dias <= DIAS_PROXIMOS:

                estado = 'proxima'
                estado_texto = 'Próxima a vencer'

                if dias == 0:
                    descripcion = '¡Vence hoy!'
                elif dias == 1:
                    descripcion = 'Vence mañana'
                else:
                    descripcion = f'Vence en {dias} días'

                icono = '⏰'
                prioridad = 1

            else:

                estado = 'seguimiento'
                estado_texto = 'En seguimiento'
                descripcion = f'Vence en {dias} días'
                icono = '🔔'
                prioridad = 3

        cliente = cuenta['cliente']
        nombre = cliente['nombre']
        codigo = cliente['codigo']
        numero = cuenta['numero']

        saldo_formato = formato_pesos_recordatorio(
            saldo
        )

        total = int(cuenta['total'])

        if total > 0:

            porcentaje_pagado = round(
                (total - saldo) / total * 100
            )

            porcentaje_pagado = max(
                0, min(100, porcentaje_pagado)
            )

        else:
            porcentaje_pagado = 0

        # MENSAJE PARA COPIAR
        mensaje = (
            f'Hola {nombre}, te recordamos que '
            f'tienes un saldo pendiente de '
            f'{saldo_formato} correspondiente '
            f'a la cuenta {numero}.'
        )

        if fecha_vencimiento is not None:

            mensaje += (
                f' Su fecha de vencimiento es '
                f'{fecha_texto}.'
            )

        mensaje += (
            ' Muchas gracias por tu atención. '
            'Charcutería.'
        )

        recordatorios.append({
            'numero': numero,
            'cliente_nombre': nombre,
            'cliente_codigo': codigo,
            'saldo': saldo,
            'saldo_formato': saldo_formato,
            'total_formato': cuenta['total_formato'],
            'abonos_formato': cuenta['abonos_formato'],
            'fecha_vencimiento': fecha_texto,
            'estado': estado,
            'estado_texto': estado_texto,
            'descripcion': descripcion,
            'icono': icono,
            'prioridad': prioridad,
            'dias': dias,
            'porcentaje_pagado': porcentaje_pagado,
            'mensaje': mensaje,
        })

    # PRIMERO VENCIDAS, LUEGO PRÓXIMAS
    recordatorios.sort(
        key=lambda r: (
            r['prioridad'],
            r['dias'],
            -r['saldo']
        )
    )

    return recordatorios


# ==========================================
# PÁGINA DE RECORDATORIOS
# ==========================================

@login_required(login_url='login')
def lista_recordatorios(request):

    usuario = request.user

    autorizado = (
        usuario.is_active and
        (
            usuario.is_superuser or
            usuario.groups.filter(
                name__in=[
                    'Administrador',
                    'Trabajador'
                ]
            ).exists()
        )
    )

    if not autorizado:
        raise PermissionDenied(
            'No tienes permiso para consultar recordatorios.'
        )

    recordatorios = obtener_recordatorios()

    # RESUMEN GENERAL
    total_pendientes = len(recordatorios)

    total_vencidas = sum(
        1 for r in recordatorios
        if r['estado'] == 'vencida'
    )

    total_proximas = sum(
        1 for r in recordatorios
        if r['estado'] == 'proxima'
    )

    total_sin_fecha = sum(
        1 for r in recordatorios
        if r['estado'] == 'sin_fecha'
    )

    saldo_total = sum(
        r['saldo'] for r in recordatorios
    )

    # FILTROS
    estado = request.GET.get(
        'estado', 'todas'
    )

    busqueda = request.GET.get(
        'q', ''
    ).strip()[:100]

    estados_validos = [
        'todas',
        'vencida',
        'proxima',
        'sin_fecha',
        'seguimiento'
    ]

    if estado not in estados_validos:
        estado = 'todas'

    if estado != 'todas':

        recordatorios = [
            r for r in recordatorios
            if r['estado'] == estado
        ]

    if busqueda:

        texto = busqueda.casefold()

        recordatorios = [
            r for r in recordatorios
            if texto in (
                r['numero'] + ' ' +
                r['cliente_nombre'] + ' ' +
                r['cliente_codigo']
            ).casefold()
        ]

    return render(
        request,
        'recordatorios/lista.html',
        {
            'recordatorios': recordatorios,
            'total_pendientes': total_pendientes,
            'total_vencidas': total_vencidas,
            'total_proximas': total_proximas,
            'total_sin_fecha': total_sin_fecha,
            'saldo_total': formato_pesos_recordatorio(
                saldo_total
            ),
            'estado': estado,
            'busqueda': busqueda,
            'dias_proximos': DIAS_PROXIMOS,
        }
    )
