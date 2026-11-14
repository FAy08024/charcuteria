
from .models import TurnoEmpleado



def roles(request):

    usuario = request.user

    es_administrador = False
    es_trabajador = False

    if usuario.is_authenticated and usuario.is_active:

        es_administrador = (
            usuario.is_superuser or
            usuario.groups.filter(
                name='Administrador'
            ).exists()
        )

        es_trabajador = (
            not es_administrador and
            usuario.groups.filter(
                name='Trabajador'
            ).exists()
        )

    return {
        'es_administrador': es_administrador,
        'es_trabajador': es_trabajador,
    }




def turno_en_sesion(request):

    if not request.user.is_authenticated:
        return {
            'turno_en_sesion': None
        }

    turno = TurnoEmpleado.objects.filter(
        empleado=request.user,
        fin__isnull=True
    ).first()

    return {
        'turno_en_sesion': turno
    }
