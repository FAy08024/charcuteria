
from django import forms
from .models import IncidenciaInventario


class IncidenciaInventarioForm(forms.ModelForm):

    class Meta:
        model = IncidenciaInventario

        fields = [
            'producto_codigo',
            'tipo',
            'cantidad',
            'descripcion',
            'foto',
        ]

    def clean_foto(self):

        foto = self.cleaned_data.get('foto')

        if foto and foto.size > 3 * 1024 * 1024:
            raise forms.ValidationError(
                'La fotografía no debe superar 3 MB.'
            )

        return foto
