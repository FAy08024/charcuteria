
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from PIL import Image, UnidentifiedImageError

from .models import PerfilUsuario


Usuario = get_user_model()


ROLES_USUARIO = [
    ('Trabajador', 'Trabajador'),
    ('Administrador', 'Administrador'),
]


# CREACIÓN DE USUARIOS
class CrearPersonalForm(UserCreationForm):

    rol = forms.ChoiceField(
        choices=ROLES_USUARIO
    )

    email = forms.EmailField(
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario

        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )

    def __init__(self, *args, permitir_admin=False, **kwargs):
        super().__init__(*args, **kwargs)

        if not permitir_admin:
            self.fields['rol'].choices = [
                ('Trabajador', 'Trabajador')
            ]


# EDICIÓN DE USUARIOS
class EditarPersonalForm(forms.ModelForm):

    rol = forms.ChoiceField(
        choices=ROLES_USUARIO
    )

    email = forms.EmailField(
        required=False
    )

    class Meta:
        model = Usuario

        fields = (
            'first_name',
            'last_name',
            'email',
            'is_active',
        )

    def __init__(self, *args, permitir_admin=False, **kwargs):
        super().__init__(*args, **kwargs)

        if not permitir_admin:
            self.fields['rol'].choices = [
                ('Trabajador', 'Trabajador')
            ]

        if not self.is_bound and self.instance.pk:

            if self.instance.groups.filter(
                name='Administrador'
            ).exists():

                self.fields['rol'].initial = 'Administrador'

            else:

                self.fields['rol'].initial = 'Trabajador'


# FOTOGRAFÍA DE PERFIL
class FotoPerfilForm(forms.ModelForm):

    class Meta:
        model = PerfilUsuario

        fields = (
            'foto',
            'posicion_x',
            'posicion_y',
        )

    def clean_foto(self):

        foto = self.cleaned_data.get('foto')

        if not foto:
            return foto

        # LÍMITE DE 3 MB
        if foto.size > 3 * 1024 * 1024:

            raise forms.ValidationError(
                'La fotografía no puede superar los 3 MB.'
            )

        try:

            foto.seek(0)

            with Image.open(foto) as imagen:

                if imagen.format not in [
                    'JPEG',
                    'PNG',
                    'WEBP',
                ]:

                    raise forms.ValidationError(
                        'Utiliza una fotografía JPG, PNG o WEBP.'
                    )

                if imagen.width > 4000 or imagen.height > 4000:

                    raise forms.ValidationError(
                        'La fotografía debe ser de máximo 4000 píxeles por lado.'
                    )

                imagen.verify()

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError
        ):

            raise forms.ValidationError(
                'La fotografía seleccionada no es válida.'
            )

        finally:
            foto.seek(0)

        return foto
