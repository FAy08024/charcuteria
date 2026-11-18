
from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto

        fields = [
            'codigo',
            'nombre',
            'categoria',
            'descripcion',
            'unidad_medida',
            'precio_venta',
            'existencias',
            'stock_minimo',
            'imagen',
            'activo',
        ]

        labels = {
            'codigo': 'Código del producto',
            'nombre': 'Nombre del producto',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'unidad_medida': 'Unidad de medida',
            'precio_venta': 'Precio de venta (COP)',
            'existencias': 'Existencias iniciales',
            'stock_minimo': 'Stock mínimo',
            'imagen': 'Imagen del producto',
            'activo': 'Producto activo',
        }

        widgets = {
            'codigo': forms.TextInput(attrs={
                'placeholder': 'PRO-006',
            }),
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej. Salchicha artesanal',
            }),
            'categoria': forms.TextInput(attrs={
                'placeholder': 'Ej. Embutidos',
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descripción del producto',
            }),
            'unidad_medida': forms.Select(choices=[
                ('unidad', 'Unidad'),
                ('kg', 'Kilogramo'),
                ('paquete', 'Paquete'),
            ]),
            'precio_venta': forms.NumberInput(attrs={
                'min': '0.01',
                'step': '0.01',
            }),
            'existencias': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.001',
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.001',
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
            }),
        }

    def clean_codigo(self):
        return self.cleaned_data['codigo'].strip().upper()

class ProductoEditarForm(forms.ModelForm):

    class Meta:
        model = Producto

        fields = [
            'precio_venta',
            'descripcion',
            'descuento',
        ]
