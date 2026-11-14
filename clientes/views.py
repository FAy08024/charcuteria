
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render


# DATOS FICTICIOS PARA PROBAR LA INTERFAZ
CLIENTES_DEMO = [
    {
        'id': 1,
        'codigo': 'CLI-001',
        'nombre': 'Lara Greyrat',
        'iniciales': 'LG',
        'tipo': 'Mayorista',
        'estado': 'Activo',
        'fecha': '04/11/2026',
        'foto': "img/Lara.jpg",
    },
    {
        'id': 2,
        'codigo': 'CLI-002',
        'nombre': 'Daniel Rojas',
        'iniciales': 'DR',
        'tipo': 'Minorista',
        'estado': 'Activo',
        'fecha': '06/11/2026',
        'foto': "img/DIOS.jpg",
    },
    {
        'id': 3,
        'codigo': 'CLI-003',
        'nombre': 'Camila Torres',
        'iniciales': 'CT',
        'tipo': 'Mayorista',
        'estado': 'Activo',
        'fecha': '09/11/2026',
        'foto': "img/April.jpg",
    },
    {
        'id': 4,
        'codigo': 'CLI-004',
        'nombre': 'Andrés Peña',
        'iniciales': 'AP',
        'tipo': 'Minorista',
        'estado': 'Activo',
        'fecha': '10/11/2026',
        'foto': "img/Soy.jpg",
    },
    {
        'id': 5,
        'codigo': 'CLI-005',
        'nombre': 'Juliana Pardo',
        'iniciales': 'JP',
        'tipo': 'Mayorista',
        'estado': 'Inactivo',
        'fecha': '11/11/2026',
        'foto': "img/xdxdxd.png",
    },
    {
        'id': 6,
        'codigo': 'CLI-006',
        'nombre': 'Nicolás Cárdenas',
        'iniciales': 'NC',
        'tipo': 'Minorista',
        'estado': 'Activo',
        'fecha': '12/11/2026',
        'foto': "img/Pure.jpg",
    },
]


def verificar_rol_clientes(usuario):
    autorizado = (
        usuario.is_superuser or
        usuario.groups.filter(
            name__in=['Administrador', 'Trabajador']
        ).exists()
    )

    if not autorizado:
        raise PermissionDenied(
            'No tienes permiso para consultar clientes.'
        )


@login_required(login_url='login')
def lista_clientes_demo(request):
    verificar_rol_clientes(request.user)

    return render(request, 'clientes/lista_demo.html', {
        'clientes': CLIENTES_DEMO
    })



@login_required(login_url='login')
def detalle_cliente_demo(request, cliente_id):

    verificar_rol_clientes(request.user)

    cliente = next(
        (
            c for c in CLIENTES_DEMO
            if c['id'] == cliente_id
        ),
        None
    )

    if cliente is None:
        raise Http404('Cliente no encontrado.')


    from cuentas.views import obtener_cuentas_agrupadas

    resumen_cuenta = next(
        (
            cuenta
            for cuenta in obtener_cuentas_agrupadas()
            if cuenta['cliente_id'] == cliente_id
        ),
        None
    )

    return render(
        request,
        'clientes/detalle_demo.html',
        {
            'cliente': cliente,
            'resumen_cuenta': resumen_cuenta,
            'creditos_cliente': (
                resumen_cuenta['creditos']
                if resumen_cuenta else []
            ),
        }
    )
