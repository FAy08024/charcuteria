from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from .forms import ClienteForm
from .models import Cliente


def es_administrador(usuario):
    return (
        usuario.is_authenticated
        and usuario.is_active
        and (
            usuario.is_superuser
            or usuario.groups.filter(
                name='Administrador'
            ).exists()
        )
    )


def verificar_rol_clientes(usuario):
    permitido = (
        usuario.is_authenticated
        and usuario.is_active
        and (
            es_administrador(usuario)
            or usuario.groups.filter(
                name='Trabajador'
            ).exists()
        )
    )

    if not permitido:
        raise PermissionDenied(
            'No tienes permiso para gestionar clientes.'
        )


# LISTADO REAL DE CLIENTES
@login_required(login_url='login')
def lista_clientes_demo(request):

    verificar_rol_clientes(request.user)

    clientes = Cliente.objects.all().order_by('nombre')

    return render(
        request,
        'clientes/lista_demo.html',
        {'clientes': clientes}
    )


# REGISTRAR CLIENTE
@login_required(login_url='login')
def crear_cliente(request):

    verificar_rol_clientes(request.user)

    formulario = ClienteForm(
        request.POST or None
    )

    if request.method == 'POST':
        if formulario.is_valid():

            cliente = formulario.save(commit=False)
            cliente.tipo = 'MINORISTA'
            cliente.estado = 'ACTIVO'
            cliente.save()

            messages.success(
                request,
                'Cliente registrado correctamente.'
            )

            return redirect('clientes_demo')

    return render(
        request,
        'clientes/formulario.html',
        {
            'formulario': formulario,
            'titulo': 'Registrar cliente',
            'boton': 'Guardar cliente',
        }
    )


# EDITAR DATOS BÁSICOS
@login_required(login_url='login')
def editar_cliente(request, cliente_id):

    verificar_rol_clientes(request.user)

    cliente = get_object_or_404(
        Cliente,
        pk=cliente_id
    )

    formulario = ClienteForm(
        request.POST or None,
        instance=cliente
    )

    if request.method == 'POST':
        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                'Datos del cliente actualizados.'
            )

            return redirect(
                'cliente_demo_detalle',
                cliente_id=cliente.pk
            )

    return render(
        request,
        'clientes/formulario.html',
        {
            'formulario': formulario,
            'titulo': 'Editar cliente',
            'boton': 'Guardar cambios',
        }
    )


# CAMBIAR TIPO Y ESTADO: SOLO ADMIN
@login_required(login_url='login')
@require_POST
def cambiar_tipo_estado(request, cliente_id):

    if not es_administrador(request.user):
        raise PermissionDenied(
            'Solo el administrador puede autorizar mayoristas.'
        )

    cliente = get_object_or_404(
        Cliente,
        pk=cliente_id
    )

    tipo = request.POST.get('tipo', '')
    estado = request.POST.get('estado', '')

    tipos_validos = {
        'MINORISTA', 'MAYORISTA'
    }
    estados_validos = {
        'ACTIVO', 'BLOQUEADO', 'INACTIVO'
    }

    if (
        tipo not in tipos_validos
        or estado not in estados_validos
    ):
        messages.error(
            request,
            'Tipo o estado de cliente inválido.'
        )

    else:
        cliente.tipo = tipo
        cliente.estado = estado

        cliente.save(
            update_fields=['tipo', 'estado']
        )

        messages.success(
            request,
            'Clasificación del cliente actualizada.'
        )

    return redirect(
        'cliente_demo_detalle',
        cliente_id=cliente.pk
    )


# PERFIL REAL DEL CLIENTE
@login_required(login_url='login')
def detalle_cliente_demo(request, cliente_id):

    verificar_rol_clientes(request.user)

    cliente = get_object_or_404(
        Cliente,
        pk=cliente_id
    )

    # Importación interna para evitar
    # dependencias circulares entre aplicaciones.
    from cuentas.views import obtener_cuentas_agrupadas

    resumen = next(
        (
            cuenta
            for cuenta in obtener_cuentas_agrupadas()
            if cuenta['cliente_id'] == cliente.pk
        ),
        None
    )

    return render(
        request,
        'clientes/detalle_demo.html',
        {
            'cliente': cliente,
            'resumen_cuenta': resumen,
            'creditos_cliente': (
                resumen['creditos']
                if resumen else []
            ),
        }
    )
