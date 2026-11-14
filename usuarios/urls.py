
from django.urls import path
from . import views


urlpatterns = [

    # INICIAR SESIÓN
    path(
        'login/',
        views.iniciar_sesion,
        name='login'
    ),

    # CERRAR SESIÓN
    path(
        'logout/',
        views.cerrar_sesion,
        name='logout'
    ),

    # PANEL SEGÚN EL ROL
    path(
        'panel/',
        views.panel_usuario,
        name='panel_usuario'
    ),

    # PANEL DE ADMINISTRADOR
    path(
        'panel/administrador/',
        views.panel_administrador,
        name='panel_administrador'
    ),

    # PANEL DE EMPLEADO
    path(
        'panel/empleado/',
        views.panel_empleado,
        name='panel_empleado'
    ),

    # DIRECTORIO DE USUARIOS
    path(
        'gestion/',
        views.gestion_usuarios,
        name='gestion_usuarios'
    ),

    # CREAR USUARIOS
    path(
        'gestion/crear/',
        views.crear_usuario_gestion,
        name='crear_usuario_gestion'
    ),

    # EDITAR USUARIOS
    path(
        'gestion/<int:usuario_id>/editar/',
        views.editar_usuario_gestion,
        name='editar_usuario_gestion'
    ),

    # CAMBIAR CONTRASEÑA
    path(
        'gestion/<int:usuario_id>/clave/',
        views.clave_usuario_gestion,
        name='clave_usuario_gestion'
    ),

    # FOTOGRAFÍA PERSONAL
    path(
        'mi-foto/',
        views.actualizar_mi_foto,
        name='actualizar_mi_foto'
    ),

    # MI JORNADA DEL EMPLEADO
    path(
        'mi-jornada/',
        views.mi_jornada,
        name='mi_jornada'
    ),

    path(
        'turno/iniciar/',
        views.iniciar_turno,
        name='iniciar_turno'
    ),

    path(
        'turno/finalizar/',
        views.finalizar_turno,
        name='finalizar_turno'
    ),


    path(
        'resumen-dia/',
        views.resumen_dia,
        name='resumen_dia'
    ),



]
