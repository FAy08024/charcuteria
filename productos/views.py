
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.templatetags.static import static


# PRODUCTOS FICTICIOS PARA ADMINISTRACIÓN
PRODUCTOS_GESTION_DEMO = [
    {
        'id': 1,
        'codigo': 'PRO-001',
        'nombre': 'Jamón especial',
        'categoria': 'Jamones',
        'descripcion': 'Jamón seleccionado de excelente calidad, ideal para compartir en familia.',
        'precio': 35000,
        'descuento': 0,
        'imagen': static('img/jamon.png'),
        'icono': '🥩',
        'tipo': 'individual',
        'componentes': [],
    },
    {
        'id': 2,
        'codigo': 'PRO-002',
        'nombre': 'Queso fresco',
        'categoria': 'Quesos',
        'descripcion': 'Queso fresco ideal para acompañar desayunos, mercados y preparaciones.',
        'precio': 24000,
        'descuento': 0,
        'imagen': '',
        'icono': '🧀',
        'tipo': 'individual',
        'componentes': [],
    },
    {
        'id': 3,
        'codigo': 'PRO-003',
        'nombre': 'Chorizo artesanal',
        'categoria': 'Chorizos',
        'descripcion': 'Chorizo de sabor tradicional, perfecto para asados y reuniones.',
        'precio': 29000,
        'descuento': 10,
        'imagen': static('img/chorizo.png'),
        'icono': '🌭',
        'tipo': 'individual',
        'componentes': [],
    },
    {
        'id': 4,
        'codigo': 'PRO-004',
        'nombre': 'Mercado familiar',
        'categoria': 'Mercados',
        'descripcion': 'Selección de alimentos y productos esenciales para el hogar.',
        'precio': 110000,
        'descuento': 0,
        'imagen': static('img/mercado.png'),
        'icono': '🛒',
        'tipo': 'individual',
        'componentes': [],
    },
    {
        'id': 5,
        'codigo': 'PRO-005',
        'nombre': 'Combo especial',
        'categoria': 'Combos',
        'descripcion': 'Selección especial de productos de nuestra charcutería.',
        'precio': 84000,
        'descuento': 0,
        'imagen': static('img/combo.png'),
        'icono': '🎁',
        'tipo': 'individual',
        'componentes': [],
    },
]


# VISTA DE ADMINISTRACIÓN DE PRODUCTOS
@login_required(login_url='login')
def productos_demo(request):

    usuario = request.user

    es_administrador = (
        usuario.is_superuser or
        usuario.groups.filter(name='Administrador').exists()
    )

    if not es_administrador:
        raise PermissionDenied(
            'Solo el administrador puede gestionar productos.'
        )

    return render(request, 'productos/productos_demo.html', {
        'productos': PRODUCTOS_GESTION_DEMO
    })
