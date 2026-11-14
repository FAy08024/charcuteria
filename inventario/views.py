
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import IncidenciaInventarioForm
from .models import AjusteExistencia, IncidenciaInventario


# PRODUCTOS FICTICIOS DEL INVENTARIO
PRODUCTOS_INVENTARIO_DEMO = [
    {
        'id': 1,
        'codigo': 'INV-001',
        'nombre': 'Jamón especial',
        'categoria': 'Jamones',
        'imagen': 'img/jamon.png',
        'stock': 18,
        'minimo': 8,
        'unidad': 'paquetes',
        'proveedor': 'Proveedor de demostración A',
        'ultima_entrada': '10/11/2026',
        'descripcion': 'Jamón seleccionado para la venta en la charcutería.',
    },
    {
        'id': 2,
        'codigo': 'INV-002',
        'nombre': 'Chorizo artesanal',
        'categoria': 'Chorizos',
        'imagen': 'img/chorizo.png',
        'stock': 7,
        'minimo': 10,
        'unidad': 'paquetes',
        'proveedor': 'Proveedor de demostración B',
        'ultima_entrada': '09/11/2026',
        'descripcion': 'Chorizo artesanal disponible para mercados y pedidos.',
    },
    {
        'id': 3,
        'codigo': 'INV-003',
        'nombre': 'Mercado familiar',
        'categoria': 'Mercados',
        'imagen': 'img/mercado.png',
        'stock': 24,
        'minimo': 8,
        'unidad': 'mercados',
        'proveedor': 'Proveedor de demostración C',
        'ultima_entrada': '11/11/2026',
        'descripcion': 'Mercado familiar con una selección de productos para el hogar.',
    },
    {
        'id': 4,
        'codigo': 'INV-004',
        'nombre': 'Combo especial',
        'categoria': 'Combos',
        'imagen': 'img/combo.png',
        'stock': 0,
        'minimo': 5,
        'unidad': 'combos',
        'proveedor': 'Proveedor de demostración D',
        'ultima_entrada': '05/11/2026',
        'descripcion': 'Combo de productos especiales de la charcutería.',
    },
]


# ENTRADAS FICTICIAS
ENTRADAS_INVENTARIO_DEMO = [
    {
        'producto': 'Mercado familiar',
        'cantidad': 12,
        'fecha': '11/11/2026',
    },
    {
        'producto': 'Jamón especial',
        'cantidad': 10,
        'fecha': '10/11/2026',
    },
    {
        'producto': 'Chorizo artesanal',
        'cantidad': 5,
        'fecha': '09/11/2026',
    },
]

# ==========================================
# PERMISOS DE INVENTARIO
# ==========================================

def es_administrador_inventario(usuario):

    return (
        usuario.is_authenticated and
        usuario.is_active and
        (
            usuario.is_superuser or
            usuario.groups.filter(
                name='Administrador'
            ).exists()
        )
    )


def es_empleado_inventario(usuario):

    return (
        usuario.is_authenticated and
        usuario.is_active and
        usuario.groups.filter(
            name='Trabajador'
        ).exists() and
        not usuario.is_superuser
    )


# ==========================================
# STOCK ACTUALIZADO
# ==========================================

def obtener_productos_inventario():

    ajustes = {
        ajuste.codigo: ajuste.diferencia
        for ajuste in AjusteExistencia.objects.all()
    }

    productos = []

    for producto in PRODUCTOS_INVENTARIO_DEMO:

        datos = producto.copy()

        datos['stock'] = max(
            0,
            producto['stock'] +
            ajustes.get(producto['codigo'], 0)
        )

        if datos['stock'] == 0:

            datos['estado'] = 'agotado'
            datos['estado_texto'] = 'Agotado'

        elif datos['stock'] <= datos['minimo']:

            datos['estado'] = 'bajo'
            datos['estado_texto'] = 'Stock bajo'

        else:

            datos['estado'] = 'disponible'
            datos['estado_texto'] = 'Disponible'

        productos.append(datos)

    return productos


# ==========================================
# MI ALMACÉN - EMPLEADO
# ==========================================

@login_required(login_url='login')
def mi_almacen(request):

    if not es_empleado_inventario(request.user):
        raise PermissionDenied(
            'Esta sección es exclusiva de trabajadores.'
        )

    productos = obtener_productos_inventario()

    formulario = IncidenciaInventarioForm()

    if request.method == 'POST':

        formulario = IncidenciaInventarioForm(
            request.POST,
            request.FILES
        )

        if formulario.is_valid():

            codigo = formulario.cleaned_data[
                'producto_codigo'
            ]

            producto = next(
                (
                    p for p in productos
                    if p['codigo'] == codigo
                ),
                None
            )

            if producto is None:

                formulario.add_error(
                    'producto_codigo',
                    'Selecciona un producto válido.'
                )

            else:

                incidencia = formulario.save(
                    commit=False
                )

                if (
                    incidencia.tipo == 'danado' and
                    incidencia.cantidad > producto['stock']
                ):

                    formulario.add_error(
                        'cantidad',
                        'No puedes reportar más unidades '
                        'dañadas que las existentes.'
                    )

                else:

                    incidencia.producto_nombre = producto[
                        'nombre'
                    ]

                    incidencia.empleado = request.user
                    incidencia.estado = 'pendiente'

                    incidencia.save()

                    messages.success(
                        request,
                        '¡Reporte enviado al administrador!'
                    )

                    return redirect('mi_almacen')

    mis_reportes = IncidenciaInventario.objects.filter(
        empleado=request.user
    )

    resumen = {
        'productos': len(productos),
        'stock_bajo': sum(
            1 for p in productos
            if p['estado'] in ['bajo', 'agotado']
        ),
        'reportes_pendientes': mis_reportes.filter(
            estado__in=['pendiente', 'revision']
        ).count(),
    }

    return render(
        request,
        'inventario/mi_almacen.html',
        {
            'productos': productos,
            'formulario': formulario,
            'reportes': mis_reportes[:20],
            'resumen': resumen,
        }
    )

# ==========================================
# BANDEJA DE INCIDENCIAS DEL ADMINISTRADOR
# ==========================================

@login_required(login_url='login')
def incidencias_admin(request):

    if not es_administrador_inventario(request.user):
        raise PermissionDenied(
            'Solo el administrador puede revisar incidencias.'
        )

    incidencias = IncidenciaInventario.objects.select_related(
        'empleado',
        'resuelto_por'
    ).all()[:100]

    pendientes = IncidenciaInventario.objects.filter(
        estado__in=['pendiente', 'revision']
    ).count()

    return render(
        request,
        'inventario/incidencias_admin.html',
        {
            'incidencias': incidencias,
            'pendientes': pendientes,
            'productos': obtener_productos_inventario(),
        }
    )


# ==========================================
# RESOLVER INCIDENCIA Y ACTUALIZAR STOCK
# ==========================================

@login_required(login_url='login')
@require_POST
def resolver_incidencia(request, incidencia_id):

    if not es_administrador_inventario(request.user):
        raise PermissionDenied(
            'No tienes permiso para resolver incidencias.'
        )

    accion = request.POST.get('accion', '').strip()

    respuesta = request.POST.get(
        'respuesta', ''
    ).strip()[:700]

    codigo_reemplazo = request.POST.get(
        'codigo_reemplazo', ''
    ).strip()

    if accion not in [
        'revision',
        'baja',
        'reemplazar',
        'descartar'
    ]:

        messages.error(
            request,
            'Selecciona una acción válida.'
        )

        return redirect('inventario_incidencias')

    if accion == 'descartar' and not respuesta:

        messages.error(
            request,
            'Explica por qué se descarta el reporte.'
        )

        return redirect('inventario_incidencias')

    with transaction.atomic():

        incidencia = get_object_or_404(
            IncidenciaInventario.objects.select_for_update(),
            pk=incidencia_id
        )

        if incidencia.estado in ['resuelta', 'descartada']:

            messages.error(
                request,
                'Esta incidencia ya fue cerrada.'
            )

            return redirect('inventario_incidencias')

        if accion == 'revision':

            incidencia.estado = 'revision'
            incidencia.respuesta = respuesta

            incidencia.save(
                update_fields=['estado', 'respuesta']
            )

            messages.success(
                request,
                'La incidencia quedó en revisión.'
            )

            return redirect('inventario_incidencias')

        if accion in ['baja', 'reemplazar']:

            productos = {
                p['codigo']: p
                for p in obtener_productos_inventario()
            }

            original = productos.get(
                incidencia.producto_codigo
            )

            if original is None:

                messages.error(
                    request,
                    'El producto reportado ya no existe.'
                )

                return redirect('inventario_incidencias')

            cantidad = incidencia.cantidad

            if original['stock'] < cantidad:

                messages.error(
                    request,
                    'No hay suficientes unidades para '
                    'realizar este ajuste.'
                )

                return redirect('inventario_incidencias')

            cambios = {
                incidencia.producto_codigo: -cantidad
            }

            if accion == 'reemplazar':

                if codigo_reemplazo not in productos:

                    messages.error(
                        request,
                        'Selecciona un producto de reemplazo válido.'
                    )

                    return redirect('inventario_incidencias')

                # SALE LA MERCANCÍA AFECTADA Y ENTRA
                # MERCANCÍA SANA FÍSICAMENTE RECIBIDA.
                cambios[codigo_reemplazo] = (
                    cambios.get(codigo_reemplazo, 0)
                    + cantidad
                )

            for codigo, diferencia in cambios.items():

                if diferencia == 0:
                    continue

                AjusteExistencia.objects.get_or_create(
                    codigo=codigo
                )

                AjusteExistencia.objects.filter(
                    codigo=codigo
                ).update(
                    diferencia=F('diferencia') + diferencia
                )

        # CERRAR EL REPORTE
        incidencia.estado = (
            'descartada'
            if accion == 'descartar'
            else 'resuelta'
        )

        incidencia.accion = accion

        incidencia.codigo_reemplazo = (
            codigo_reemplazo
            if accion == 'reemplazar'
            else ''
        )

        incidencia.respuesta = respuesta
        incidencia.resuelto_por = request.user
        incidencia.fecha_resolucion = timezone.now()

        incidencia.save()

    messages.success(
        request,
        'La incidencia se procesó correctamente.'
    )

    return redirect('inventario_incidencias')


@login_required(login_url='login')
def inventario_demo(request):

    usuario = request.user

    es_administrador = (
        usuario.is_superuser or
        usuario.groups.filter(
            name='Administrador'
        ).exists()
    )

    if not es_administrador:
        raise PermissionDenied(
            'Solo el administrador puede acceder a este inventario.'
        )

    productos = obtener_productos_inventario()

    resumen = {
        'total_productos': len(productos),
        'total_unidades': sum(p['stock'] for p in productos),
        'stock_bajo': sum(
            1 for p in productos if p['estado'] == 'bajo'
        ),
        'agotados': sum(
            1 for p in productos if p['estado'] == 'agotado'
        ),
    }

    return render(request, 'inventario/inventario_demo.html', {
        'productos': productos,
        'entradas': ENTRADAS_INVENTARIO_DEMO,
        'resumen': resumen,
    })
