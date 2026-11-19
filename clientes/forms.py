
from django import forms
from django.core.exceptions import ValidationError

from .models import Cliente


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente

        fields = [
            'nombre',
            'documento',
            'telefono',
            'direccion',
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nombre completo',
            }),
            'documento': forms.TextInput(attrs={
                'placeholder': 'Documento de identidad',
            }),
            'telefono': forms.TextInput(attrs={
                'placeholder': 'Número de contacto',
            }),
            'direccion': forms.TextInput(attrs={
                'placeholder': 'Dirección del cliente',
            }),
        }

    def clean_documento(self):
        documento = (
            self.cleaned_data['documento']
            .strip().upper()
        )

        duplicado = Cliente.objects.filter(
            documento__iexact=documento
        ).exclude(pk=self.instance.pk).exists()

        if duplicado:
            raise ValidationError(
                'Ya existe un cliente con este documento.'
            )

        return documento
