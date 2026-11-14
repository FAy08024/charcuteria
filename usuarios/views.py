

from datetime import timedelta
from .models import TurnoEmpleado
from django.utils import timezone
from ventas.models import Venta
from cuentas.models import Abono
from inventario.models import IncidenciaInventario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.views.decorators.http import require_POST

from .forms import (
    CrearPersonalForm,
    EditarPersonalForm,
    FotoPerfilForm
)

from .models import (
    ActividadUsuario,
    PerfilUsuario
)








# ==========================================
# ROLES Y AUTORIZACIÓN
# ==========================================

def rol_del_usuario(usuario):

    if usuario.is_superuser:
        return 'Superadministrador'

    if usuario.groups.filter(
        name='Administrador'
    ).exists():
        return 'Administrador'

    if usuario.groups.filter(
        name='Trabajador'
    ).exists():
        return 'Trabajador'

    return 'Sin asignar'


def es_gestor_personal(usuario):

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


def verificar_gestor_personal(usuario):

    if not es_gestor_personal(usuario):

        raise PermissionDenied(
            'No tienes permiso para administrar usuarios.'
        )


def puede_editar_personal(actor, objetivo):

    # No modificamos cuentas de superadministrador
    # desde este formulario.
    if objetivo.is_superuser:
        return False

    # El usuario no puede modificar sus propios
    # roles ni desactivar su cuenta desde aquí.
    if actor.pk == objetivo.pk:
        return False

    if actor.is_superuser:
        return True

    return (
        es_gestor_personal(actor) and
        rol_del_usuario(objetivo) == 'Trabajador'
    )


def verificar_edicion_personal(actor, objetivo):

    if not puede_editar_personal(actor, objetivo):

        raise PermissionDenied(
            'No puedes modificar esta cuenta.'
        )


def asignar_rol_personal(usuario, nombre_rol):

    grupo, creado = Group.objects.get_or_create(
        name=nombre_rol
    )

    grupos_anteriores = Group.objects.filter(
        name__in=['Administrador', 'Trabajador']
    )

    usuario.groups.remove(*grupos_anteriores)
    usuario.groups.add(grupo)


# ==========================================
# INICIAR SESIÓN
# ==========================================

def iniciar_sesion(request):

    if request.user.is_authenticated:
        return redirect('inicio')

    error = None

    if request.method == 'POST':

        username = request.POST.get(
            'username', ''
        ).strip()

        password = request.POST.get(
            'password', ''
        )

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:

            login(request, usuario)

            return redirect('inicio')

        error = 'Usuario o contraseña incorrectos.'

    return render(
        request,
        'usuarios/login.html',
        {'error': error}
    )


# ==========================================
# CERRAR SESIÓN
# ==========================================


# ==========================================
# CERRAR SESIÓN
# ==========================================

@require_POST
def cerrar_sesion(request):

    if request.user.is_authenticated:

        turno = obtener_turno_abierto(request.user)

        if turno:

            messages.warning(
                request,
                'Debes finalizar tu turno antes de cerrar sesión.'
            )

            return redirect('panel_empleado')

    logout(request)

    return redirect('inicio')


# ==========================================
# PANEL SEGÚN EL ROL
# ==========================================

@login_required(login_url='login')
def panel_usuario(request):

    rol = rol_del_usuario(request.user)

    if rol in ['Administrador', 'Superadministrador']:
        return redirect('panel_administrador')

    if rol == 'Trabajador':
        return redirect('panel_empleado')

    raise PermissionDenied(
        'Tu cuenta no tiene un rol asignado.'
    )



@login_required(login_url='login')
def panel_administrador(request):

    verificar_gestor_personal(request.user)

    alertas = IncidenciaInventario.objects.filter(
        estado__in=['pendiente', 'revision']
    ).count()

    turnos_pendientes = TurnoEmpleado.objects.filter(
        fin__isnull=False,
        revisado_admin=False
    ).count()

    return render(
        request,
        'usuarios/panel_administrador.html',
        {
            'alertas_inventario': alertas,
            'alertas_turnos': turnos_pendientes
        }
    )



@login_required(login_url='login')
def panel_empleado(request):

    if rol_del_usuario(request.user) != 'Trabajador':
        raise PermissionDenied(
            'Esta sección es para trabajadores.'
        )

    turno = obtener_turno_abierto(request.user)

    return render(
        request,
        'usuarios/panel_empleado.html',
        {
            'turno_abierto': turno
        }
    )


# ==========================================
# DATOS DEL DIRECTORIO DE USUARIOS
# ==========================================

def contexto_gestion_personal(
    request,
    formulario=None,
    abrir_crear=False
):

    Usuario = get_user_model()

    usuarios_db = list(
        Usuario.objects.prefetch_related(
            'groups'
        ).order_by('username')
    )

    perfiles = {
        perfil.usuario_id: perfil
        for perfil in PerfilUsuario.objects.all()
    }

    usuarios = []

    for usuario in usuarios_db:

        perfil = perfiles.get(usuario.pk)

        foto_url = ''
        posicion_x = 50
        posicion_y = 50

        if perfil:

            posicion_x = perfil.posicion_x
            posicion_y = perfil.posicion_y

            if perfil.foto:
                foto_url = perfil.foto.url

        usuarios.append({
            'usuario': usuario,
            'rol': rol_del_usuario(usuario),
            'editable': puede_editar_personal(
                request.user,
                usuario
            ),
            'es_mio': request.user.pk == usuario.pk,
            'foto_url': foto_url,
            'posicion_x': posicion_x,
            'posicion_y': posicion_y,
        })

    mi_perfil = perfiles.get(request.user.pk)

    mi_foto_url = ''
    mi_pos_x = 50
    mi_pos_y = 50

    if mi_perfil:

        mi_pos_x = mi_perfil.posicion_x
        mi_pos_y = mi_perfil.posicion_y

        if mi_perfil.foto:
            mi_foto_url = mi_perfil.foto.url

    actividades = ActividadUsuario.objects.select_related(
        'actor',
        'usuario_objetivo'
    )[:10]

    return {
        'usuarios': usuarios,
        'actividades': actividades,
        'total_usuarios': len(usuarios),
        'total_activos': sum(
            1 for item in usuarios
            if item['usuario'].is_active
        ),
        'total_administradores': sum(
            1 for item in usuarios
            if item['rol'] in [
                'Administrador',
                'Superadministrador'
            ]
        ),
        'total_trabajadores': sum(
            1 for item in usuarios
            if item['rol'] == 'Trabajador'
        ),
        'formulario': formulario or CrearPersonalForm(
            permitir_admin=request.user.is_superuser
        ),
        'abrir_crear': abrir_crear,
        'puede_crear_admin': request.user.is_superuser,
        'mi_foto_url': mi_foto_url,
        'mi_pos_x': mi_pos_x,
        'mi_pos_y': mi_pos_y,
    }


# ==========================================
# VER USUARIOS Y PERMISOS
# ==========================================

@login_required(login_url='login')
def gestion_usuarios(request):

    verificar_gestor_personal(request.user)

    return render(
        request,
        'usuarios/gestion_usuarios.html',
        contexto_gestion_personal(request)
    )


# ==========================================
# CREAR USUARIO
# ==========================================

@login_required(login_url='login')
@require_POST
def crear_usuario_gestion(request):

    verificar_gestor_personal(request.user)

    formulario = CrearPersonalForm(
        request.POST,
        permitir_admin=request.user.is_superuser
    )

    if formulario.is_valid():

        with transaction.atomic():

            usuario = formulario.save(commit=False)

            usuario.is_active = True
            usuario.is_staff = False
            usuario.is_superuser = False

            usuario.save()

            rol = formulario.cleaned_data['rol']

            asignar_rol_personal(usuario, rol)

            ActividadUsuario.objects.create(
                actor=request.user,
                usuario_objetivo=usuario,
                accion='Creación',
                detalle=(
                    'Se creó la cuenta ' +
                    usuario.username +
                    ' con el rol ' + rol
                )
            )

        messages.success(
            request,
            'Usuario creado correctamente.'
        )

        return redirect('gestion_usuarios')

    return render(
        request,
        'usuarios/gestion_usuarios.html',
        contexto_gestion_personal(
            request,
            formulario=formulario,
            abrir_crear=True
        ),
        status=400
    )


# ==========================================
# EDITAR USUARIO
# ==========================================

@login_required(login_url='login')
@require_POST
def editar_usuario_gestion(request, usuario_id):

    verificar_gestor_personal(request.user)

    Usuario = get_user_model()

    objetivo = get_object_or_404(
        Usuario,
        pk=usuario_id
    )

    verificar_edicion_personal(
        request.user,
        objetivo
    )

    formulario = EditarPersonalForm(
        request.POST,
        instance=objetivo,
        permitir_admin=request.user.is_superuser
    )

    if formulario.is_valid():

        with transaction.atomic():

            usuario = formulario.save()

            nuevo_rol = formulario.cleaned_data['rol']

            asignar_rol_personal(
                usuario,
                nuevo_rol
            )

            ActividadUsuario.objects.create(
                actor=request.user,
                usuario_objetivo=usuario,
                accion='Edición',
                detalle=(
                    'Se modificó la cuenta ' +
                    usuario.username +
                    '. Rol: ' + nuevo_rol
                )
            )

        messages.success(
            request,
            'Usuario actualizado correctamente.'
        )

    else:

        for errores in formulario.errors.values():
            for error in errores:
                messages.error(request, str(error))

    return redirect('gestion_usuarios')


# ==========================================
# CAMBIAR CONTRASEÑA DE UN USUARIO
# ==========================================

@login_required(login_url='login')
@require_POST
def clave_usuario_gestion(request, usuario_id):

    verificar_gestor_personal(request.user)

    Usuario = get_user_model()

    objetivo = get_object_or_404(
        Usuario,
        pk=usuario_id
    )

    verificar_edicion_personal(
        request.user,
        objetivo
    )

    formulario = SetPasswordForm(
        objetivo,
        request.POST
    )

    if formulario.is_valid():

        with transaction.atomic():

            formulario.save()

            ActividadUsuario.objects.create(
                actor=request.user,
                usuario_objetivo=objetivo,
                accion='Contraseña',
                detalle=(
                    'Se restableció la contraseña de ' +
                    objetivo.username
                )
            )

        messages.success(
            request,
            'Contraseña actualizada correctamente.'
        )

    else:

        for errores in formulario.errors.values():
            for error in errores:
                messages.error(request, str(error))

    return redirect('gestion_usuarios')


# ==========================================
# ACTUALIZAR MI FOTO DE PERFIL
# ==========================================

@login_required(login_url='login')
@require_POST
def actualizar_mi_foto(request):

    perfil, creado = PerfilUsuario.objects.get_or_create(
        usuario=request.user
    )

    # Si todavía no hay foto, es obligatorio subir una.
    if not perfil.foto and not request.FILES.get('foto'):

        messages.error(
            request,
            'Primero debes seleccionar una fotografía.'
        )

        if es_gestor_personal(request.user):
            return redirect('gestion_usuarios')

        return redirect('panel_usuario')

    formulario = FotoPerfilForm(
        request.POST,
        request.FILES,
        instance=perfil
    )

    if formulario.is_valid():

        formulario.save()

        ActividadUsuario.objects.create(
            actor=request.user,
            usuario_objetivo=request.user,
            accion='Fotografía',
            detalle=(
                request.user.username +
                ' actualizó su fotografía de perfil.'
            )
        )

        messages.success(
            request,
            'Tu fotografía se guardó correctamente.'
        )

    else:

        for errores in formulario.errors.values():
            for error in errores:
                messages.error(request, str(error))

    if es_gestor_personal(request.user):
        return redirect('gestion_usuarios')

    return redirect('panel_usuario')

# ==========================================
# MI JORNADA - HISTORIAL DEL EMPLEADO
# ==========================================

def formato_dinero_jornada(valor):
    return '$' + format(int(valor), ',').replace(',', '.')


@login_required(login_url='login')
def mi_jornada(request):

    # SOLO PERSONAL CON ROL TRABAJADOR
    if (
        not request.user.is_active or
        rol_del_usuario(request.user) != 'Trabajador'
    ):
        raise PermissionDenied(
            'Esta sección es exclusiva de los empleados.'
        )

    periodo = request.GET.get('periodo', 'hoy')
    tipo = request.GET.get('tipo', 'todos')
    busqueda = request.GET.get('q', '').strip()[:100]

    if periodo not in ['hoy', 'ayer', '7dias', 'todos']:
        periodo = 'hoy'

    if tipo not in ['todos', 'ventas', 'abonos']:
        tipo = 'todos'

    hoy = timezone.localdate()

    # SOLO LAS OPERACIONES DEL USUARIO ACTUAL
    ventas = Venta.objects.filter(
        empleado=request.user
    ).prefetch_related('detalles')

    abonos = Abono.objects.filter(
        empleado=request.user
    )

    # FILTRO DE FECHAS
    if periodo == 'hoy':

        ventas = ventas.filter(fecha__date=hoy)
        abonos = abonos.filter(fecha__date=hoy)

    elif periodo == 'ayer':

        ayer = hoy - timedelta(days=1)

        ventas = ventas.filter(fecha__date=ayer)
        abonos = abonos.filter(fecha__date=ayer)

    elif periodo == '7dias':

        desde = hoy - timedelta(days=6)

        ventas = ventas.filter(fecha__date__gte=desde)
        abonos = abonos.filter(fecha__date__gte=desde)

    # OBTENER NOMBRES DE CLIENTES DE LOS ABONOS
    from cuentas.views import obtener_cuentas_demo

    cuentas_por_numero = {
        cuenta['numero']: cuenta
        for cuenta in obtener_cuentas_demo()
    }

    movimientos_periodo = []

    # ======================================
    # VENTAS REALIZADAS POR ESTE EMPLEADO
    # ======================================

    for venta in ventas:

        detalles = []

        for producto in venta.detalles.all():

            detalles.append({
                'nombre': producto.producto_nombre,
                'cantidad': producto.cantidad,
                'importe_formato': formato_dinero_jornada(
                    producto.importe
                ),
            })

        # SOLO VENTAS DE CONTADO COBRADAS
        cobrado = 0

        if (
            venta.tipo == 'Contado' and
            venta.estado == 'Pagada'
        ):
            cobrado = venta.total

        movimientos_periodo.append({
            'tipo': 'venta',
            'numero': venta.numero,
            'cliente': venta.cliente_nombre,
            'codigo_cliente': venta.cliente_codigo,
            'descripcion': 'Venta a ' + venta.tipo.lower(),
            'metodo': venta.metodo_pago,
            'estado': venta.estado,
            'fecha': timezone.localtime(venta.fecha),
            'monto': venta.total,
            'monto_formato': formato_dinero_jornada(
                venta.total
            ),
            'cobrado': cobrado,
            'cuenta_numero': '',
            'detalles': detalles,
        })

    # ======================================
    # ABONOS RECIBIDOS POR ESTE EMPLEADO
    # ======================================

    for abono in abonos:

        cuenta = cuentas_por_numero.get(
            abono.cuenta_numero
        )

        if cuenta:

            cliente = cuenta['cliente']['nombre']
            codigo = cuenta['cliente']['codigo']

        else:

            cliente = 'Cliente no disponible'
            codigo = 'Sin registro'

        movimientos_periodo.append({
            'tipo': 'abono',
            'numero': 'ABO-' + str(abono.pk).zfill(3),
            'cliente': cliente,
            'codigo_cliente': codigo,
            'descripcion': (
                'Abono a la cuenta ' + abono.cuenta_numero
            ),
            'metodo': abono.metodo_pago,
            'estado': 'Recibido',
            'fecha': timezone.localtime(abono.fecha),
            'monto': abono.monto,
            'monto_formato': formato_dinero_jornada(
                abono.monto
            ),
            'cobrado': abono.monto,
            'cuenta_numero': abono.cuenta_numero,
            'detalles': [],
        })

    # ======================================
    # ESTADÍSTICAS DEL PERÍODO SELECCIONADO
    # ======================================

    total_ventas = sum(
        1 for movimiento in movimientos_periodo
        if movimiento['tipo'] == 'venta'
    )

    total_abonos = sum(
        1 for movimiento in movimientos_periodo
        if movimiento['tipo'] == 'abono'
    )

    recaudado_ventas = sum(
        movimiento['cobrado']
        for movimiento in movimientos_periodo
        if movimiento['tipo'] == 'venta'
    )

    recaudado_abonos = sum(
        movimiento['cobrado']
        for movimiento in movimientos_periodo
        if movimiento['tipo'] == 'abono'
    )

    total_recaudado = (
        recaudado_ventas + recaudado_abonos
    )

    # ======================================
    # FILTRAR EL HISTORIAL VISIBLE
    # ======================================

    movimientos = movimientos_periodo

    if tipo == 'ventas':

        movimientos = [
            m for m in movimientos
            if m['tipo'] == 'venta'
        ]

    elif tipo == 'abonos':

        movimientos = [
            m for m in movimientos
            if m['tipo'] == 'abono'
        ]

    if busqueda:

        texto = busqueda.casefold()

        movimientos = [
            m for m in movimientos
            if texto in (
                m['numero'] + ' ' +
                m['cliente'] + ' ' +
                m['codigo_cliente'] + ' ' +
                m['descripcion'] + ' ' +
                m['metodo'] + ' ' +
                m['cuenta_numero']
            ).casefold()
        ]

    movimientos.sort(
        key=lambda m: m['fecha'],
        reverse=True
    )

    return render(
        request,
        'usuarios/mi_jornada.html',
        {
            'movimientos': movimientos,
            'periodo': periodo,
            'tipo': tipo,
            'busqueda': busqueda,
            'total_ventas': total_ventas,
            'total_abonos': total_abonos,
            'recaudado_ventas': formato_dinero_jornada(
                recaudado_ventas
            ),
            'recaudado_abonos': formato_dinero_jornada(
                recaudado_abonos
            ),
            'total_recaudado': formato_dinero_jornada(
                total_recaudado
            ),
        }
    )

# ==========================================
# CONTROL DE TURNOS
# ==========================================

def obtener_turno_abierto(usuario):

    if not usuario.is_authenticated:
        return None

    return TurnoEmpleado.objects.filter(
        empleado=usuario,
        fin__isnull=True
    ).first()


@login_required(login_url='login')
@require_POST
def iniciar_turno(request):

    if rol_del_usuario(request.user) != 'Trabajador':
        raise PermissionDenied(
            'Solo los trabajadores pueden iniciar turno.'
        )

    if obtener_turno_abierto(request.user):

        messages.warning(
            request,
            'Ya tienes un turno abierto.'
        )

        return redirect('panel_empleado')

    TurnoEmpleado.objects.create(
        empleado=request.user
    )

    messages.success(
        request,
        '¡Turno iniciado correctamente!'
    )

    return redirect('panel_empleado')


@login_required(login_url='login')
@require_POST
def finalizar_turno(request):

    if rol_del_usuario(request.user) != 'Trabajador':
        raise PermissionDenied(
            'Solo los trabajadores pueden finalizar turno.'
        )

    with transaction.atomic():

        turno = TurnoEmpleado.objects.select_for_update().filter(
            empleado=request.user,
            fin__isnull=True
        ).first()

        if turno is None:

            messages.error(
                request,
                'No tienes un turno abierto.'
            )

            return redirect('panel_empleado')

        fin = timezone.now()

        ventas = Venta.objects.filter(
            empleado=request.user,
            fecha__gte=turno.inicio,
            fecha__lte=fin
        )

        abonos = Abono.objects.filter(
            empleado=request.user,
            fecha__gte=turno.inicio,
            fecha__lte=fin
        )

        ventas_lista = list(ventas)
        abonos_lista = list(abonos)

        turno.cantidad_ventas = len(ventas_lista)
        turno.cantidad_abonos = len(abonos_lista)

        turno.total_ventas = sum(
            venta.total
            for venta in ventas_lista
        )

        turno.total_abonos = sum(
            abono.monto
            for abono in abonos_lista
        )

        contado_cobrado = sum(
            venta.total
            for venta in ventas_lista
            if (
                venta.tipo == 'Contado' and
                venta.estado == 'Pagada'
            )
        )

        turno.total_recaudado = (
            contado_cobrado + turno.total_abonos
        )

        turno.fin = fin
        turno.revisado_admin = False
        turno.save()


    if request.POST.get('cerrar_despues') == 'si':

        logout(request)

        messages.success(
            request,
            'Turno finalizado y sesión cerrada correctamente.'
        )

        return redirect('inicio')

    messages.success(
        request,
        'Turno finalizado. Resumen enviado al administrador.'
    )

    return redirect('panel_empleado')



@login_required(login_url='login')
def resumen_dia(request):

    if rol_del_usuario(request.user) != 'Trabajador':
        raise PermissionDenied(
            'Esta sección es exclusiva de trabajadores.'
        )

    turnos = list(
        TurnoEmpleado.objects.filter(
            empleado=request.user
        ).order_by('-inicio')[:30]
    )

    turno_id = request.GET.get('turno', '')

    if turno_id.isascii() and turno_id.isdigit():

        turno = get_object_or_404(
            TurnoEmpleado,
            pk=int(turno_id),
            empleado=request.user
        )

    else:
        turno = turnos[0] if turnos else None

    resumen = None
    movimientos = []

    if turno:

        fecha_fin = turno.fin or timezone.now()

        ventas = list(
            Venta.objects.filter(
                empleado=request.user,
                fecha__gte=turno.inicio,
                fecha__lte=fecha_fin
            ).prefetch_related('detalles')
        )

        abonos = list(
            Abono.objects.filter(
                empleado=request.user,
                fecha__gte=turno.inicio,
                fecha__lte=fecha_fin
            )
        )

        incidencias = list(
            IncidenciaInventario.objects.filter(
                empleado=request.user,
                fecha__gte=turno.inicio,
                fecha__lte=fecha_fin
            )
        )

        total_ventas = sum(v.total for v in ventas)
        total_abonos = sum(a.monto for a in abonos)

        contado_cobrado = sum(
            v.total for v in ventas
            if v.tipo == 'Contado'
            and v.estado == 'Pagada'
        )

        ventas_credito = sum(
            1 for v in ventas
            if v.tipo == 'Crédito'
        )

        if turno.fin:

            cantidad_ventas = turno.cantidad_ventas
            cantidad_abonos = turno.cantidad_abonos
            total_ventas = turno.total_ventas
            total_abonos = turno.total_abonos
            recaudado = turno.total_recaudado

        else:

            cantidad_ventas = len(ventas)
            cantidad_abonos = len(abonos)
            recaudado = contado_cobrado + total_abonos

        resumen = {
            'cantidad_ventas': cantidad_ventas,
            'cantidad_abonos': cantidad_abonos,
            'cantidad_incidencias': len(incidencias),
            'ventas_credito': ventas_credito,
            'total_ventas': formato_dinero_jornada(
                total_ventas
            ),
            'total_abonos': formato_dinero_jornada(
                total_abonos
            ),
            'recaudado': formato_dinero_jornada(
                recaudado
            ),
        }

        # MOVIMIENTOS DE VENTAS
        for venta in ventas:

            detalle = ', '.join(
                p.producto_nombre + ' x' + str(p.cantidad)
                for p in venta.detalles.all()
            )

            movimientos.append({
                'tipo': 'Venta',
                'icono': '🛒',
                'titulo': venta.numero,
                'descripcion': (
                    venta.cliente_nombre + ' · ' +
                    venta.tipo + ' · ' + detalle
                ),
                'fecha': venta.fecha,
                'valor': formato_dinero_jornada(
                    venta.total
                ),
            })

        # MOVIMIENTOS DE ABONOS
        for abono in abonos:

            movimientos.append({
                'tipo': 'Abono',
                'icono': '💳',
                'titulo': 'ABO-' + str(abono.pk).zfill(3),
                'descripcion': (
                    'Cuenta ' + abono.cuenta_numero +
                    ' · ' + abono.metodo_pago
                ),
                'fecha': abono.fecha,
                'valor': formato_dinero_jornada(
                    abono.monto
                ),
            })

        # REPORTES DE INVENTARIO
        for incidencia in incidencias:

            movimientos.append({
                'tipo': 'Inventario',
                'icono': '📦',
                'titulo': incidencia.producto_nombre,
                'descripcion': (
                    incidencia.get_tipo_display() +
                    ' · ' + str(incidencia.cantidad) +
                    ' unidades'
                ),
                'fecha': incidencia.fecha,
                'valor': 'Reporte',
            })

        movimientos.sort(
            key=lambda item: item['fecha'],
            reverse=True
        )

    return render(
        request,
        'usuarios/resumen_dia.html',
        {
            'turnos': turnos,
            'turno': turno,
            'resumen': resumen,
            'movimientos': movimientos,
        }
    )
