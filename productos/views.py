

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.templatetags.static import static
from django.views.decorators.http import require_POST

from .models import Producto
from .forms import ProductoForm
from django.urls import reverse
from .forms import ProductoForm, ProductoEditarForm
from django.shortcuts import get_object_or_404, redirect

from .models import Producto, Combo



from django.shortcuts import redirect

from .forms import ProductoEditarForm

# VISTA DE ADMINISTRACIÓN DE PRODUCTOS


# PERMISOS DE ADMINISTRADOR

# VERIFICAR PERMISOS DEL ADMINISTRADOR
def es_admin(usuario):
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


# PÁGINA DE ADMINISTRACIÓN DE PRODUCTOS
@login_required(login_url='login')
def productos_demo(request):

    if not es_admin(request.user):
        raise PermissionDenied(
            'Solo un administrador puede gestionar productos.'
        )

    return render(
        request,
        'productos/productos_demo.html',
        contexto_productos()
    )




# PRODUCTOS REALES + DEMOSTRACIÓN

def contexto_productos(form=None, abrir_modal=False):

    productos_reales = []

    iconos = {
        'Jamones': '🥩',
        'Quesos': '🧀',
        'Chorizos': '🌭',
    }

    consulta = Producto.objects.filter(
        activo=True
    ).order_by('nombre')

    for p in consulta:

        productos_reales.append({
            'id': f'real-{p.pk}',
            'db_id': p.pk,  # <-- AGREGAR ESTA LÍNEA
            'codigo': p.codigo,
            'nombre': p.nombre,
            'categoria': p.categoria or 'Sin categoría',
            'descripcion': p.descripcion or '',
            'precio': float(p.precio_venta),
            'descuento': p.descuento,
            'imagen': p.imagen.url if p.imagen else '',
            'icono': iconos.get(p.categoria, '📦'),
            'tipo': 'individual',
            'componentes': [],
            'es_real': True,
            'editar_url': reverse(
                'editar_producto',
                args=[p.pk]
            ),
        })
    
    # COMBOS GUARDADOS EN SQLITE
    combos_reales = []

    consulta_combos = Combo.objects.filter(
        activo=True
    ).select_related(
        'producto_uno',
        'producto_dos'
    )

    for c in consulta_combos:
        combos_reales.append({
            'id': f'combo-{c.pk}',
            'codigo': c.codigo,
            'nombre': c.nombre,
            'categoria': 'Combos',
            'descripcion': (
                f'Incluye {c.producto_uno.nombre} y '
                f'{c.producto_dos.nombre}. '
                'Promoción especial del 20%.'
            ),
            'precio': float(c.precio_base),
            'descuento': c.descuento,
            'imagen': '',
            'icono': '🎁',
            'tipo': 'combo',
            'componentes': [
                f'real-{c.producto_uno_id}',
                f'real-{c.producto_dos_id}'
            ],
            'es_combo_guardado': True,
            'es_real': True,
        })
    
    return {
    'productos': productos_reales + combos_reales,
    'form_producto': (
        form if form is not None else ProductoForm()
    ),
    'abrir_modal_producto': abrir_modal,
}


# PÁGINA DE ADMINISTRACIÓN DE PRODUCTOS
@login_required(login_url='login')
def productos_demo(request):

    if not es_admin(request.user):
        raise PermissionDenied(
            'Solo un administrador puede gestionar productos.'
        )

    return render(
        request,
        'productos/productos_demo.html',
        contexto_productos()
    )


# CREAR PRODUCTO EN SQLITE
@login_required(login_url='login')
@require_POST
def crear_producto(request):

    if not es_admin(request.user):
        raise PermissionDenied(
            'No tienes permiso para crear productos.'
        )

    formulario = ProductoForm(
        request.POST,
        request.FILES
    )

    if formulario.is_valid():

        producto = formulario.save()

        messages.success(
            request,
            f'Producto "{producto.nombre}" creado correctamente.'
        )

        return redirect('productos_demo')

    return render(
        request,
        'productos/productos_demo.html',
        contexto_productos(
            form=formulario,
            abrir_modal=True
        )
    )


    return render(request, 'productos/productos_demo.html', {
        'productos': PRODUCTOS_GESTION_DEMO
    })

@login_required(login_url='login')
@require_POST
def editar_producto(request, pk):

    if not es_admin(request.user):
        raise PermissionDenied(
            'Solo los administradores pueden editar productos.'
        )

    producto = get_object_or_404(
        Producto,
        pk=pk
    )

    formulario = ProductoEditarForm(
        request.POST,
        instance=producto
    )

    if formulario.is_valid():

        formulario.save()

        messages.success(
            request,
            f'Producto "{producto.nombre}" actualizado.'
        )

    else:
        mensajes = []

        for campo, errores in formulario.errors.items():
            for error in errores:
                mensajes.append(f'{campo}: {error}')

        messages.error(
            request,
            'No se pudo actualizar: ' + '; '.join(mensajes)
        )

    return redirect('productos_demo')

@login_required(login_url='login')
@require_POST
def crear_combo(request):

    if not es_admin(request.user):
        raise PermissionDenied(
            'Solo los administradores pueden crear combos.'
        )

    nombre = request.POST.get('nombre', '').strip()

    try:
        id_uno = int(request.POST.get('producto_uno', ''))
        id_dos = int(request.POST.get('producto_dos', ''))
    except (ValueError, TypeError):
        messages.error(
            request,
            'Debes seleccionar dos productos válidos.'
        )
        return redirect('productos_demo')

    if not nombre or len(nombre) > 100:
        messages.error(
            request,
            'El nombre del combo no es válido.'
        )
        return redirect('productos_demo')

    if id_uno == id_dos:
        messages.error(
            request,
            'Selecciona dos productos diferentes.'
        )
        return redirect('productos_demo')

    productos = Producto.objects.filter(
        pk__in=[id_uno, id_dos],
        activo=True
    )

    mapa = {p.pk: p for p in productos}

    if id_uno not in mapa or id_dos not in mapa:
        messages.error(
            request,
            'Uno de los productos no existe o está inactivo.'
        )
        return redirect('productos_demo')

    combo = Combo(
        nombre=nombre,
        producto_uno=mapa[id_uno],
        producto_dos=mapa[id_dos]
    )

    combo.full_clean()
    combo.save()

    messages.success(
        request,
        f'Combo {combo.codigo} creado correctamente.'
    )

    return redirect('productos_demo')
