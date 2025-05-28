from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import MensajeContacto, Producto
from django.contrib.auth.models import User
import re



# Opciones de selección
NACIONALIDADES = [
    ('chile', 'Chile'),
    ('argentina', 'Argentina'),
    ('peru', 'Perú'),
    ('mexico', 'México'),
]

SEXO_CHOICES = [
    ('masculino', 'Masculino'),
    ('femenino', 'Femenino'),
    ('otro', 'Otro'),
]




class RegistroCompletoForm(UserCreationForm):
    rut = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT (Ej: 12.345.678-9)'})
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )

    nacionalidad = forms.ChoiceField(
        choices=NACIONALIDADES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    sexo = forms.ChoiceField(
        choices=SEXO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    fecha_nacimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    celular = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número celular'})
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )

    direccion = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de despacho'})
    )

    comuna = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comuna'})
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )

    class Meta:
        model = User
        fields = ['rut', 'first_name', 'last_name', 'username', 'nacionalidad', 'sexo', 
                  'fecha_nacimiento', 'celular', 'email', 'direccion', 'comuna', 'password1', 'password2']

    def clean_rut(self):
        """Valida que el RUT tenga un formato válido."""
        rut = self.cleaned_data.get('rut')
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise ValidationError("Formato de RUT inválido. Usa el formato: 12.345.678-9")
        return rut

    def clean_celular(self):
        """Valida que el número celular tenga el formato correcto."""
        celular = self.cleaned_data.get('celular')
        if not re.match(r'^\+?56\d{8,9}$', celular):  # Formato para Chile (+56)
            raise ValidationError("Formato de celular inválido. Usa +569XXXXXXXX")
        return celular

    def clean_email(self):
        """Verifica que el email no esté registrado y tenga el formato correcto."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Formato de correo inválido.")
        return email

    def clean_password1(self):
        """Añade validaciones adicionales a la contraseña."""
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'\d', password):
            raise ValidationError("Debe contener al menos un número.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Debe contener al menos una mayúscula.")
        return password


class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'marca', 'modelo', 'precio', 'stock', 'categoria', 'imagen', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }