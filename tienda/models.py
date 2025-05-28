from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class Categoria(models.Model):
    """Modelo para categorías de productos con nombre único"""
    nombre = models.CharField(
        _('Nombre'),
        max_length=100,
        unique=True,
        help_text=_('Nombre descriptivo de la categoría')
    )

    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Modelo principal para productos de ferretería"""
    codigo = models.CharField(
        _('Código'),
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[A-Z0-9-]+$',
                message=_('Solo mayúsculas, números y guiones permitidos')
            )
        ]
    )
    nombre = models.CharField(_('Nombre'), max_length=200)
    marca = models.CharField(_('Marca'), max_length=100)
    modelo = models.CharField(_('Modelo'), max_length=100)
    precio = models.DecimalField(
        _('Precio'),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(_('Stock disponible'), default=0)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,  # Evita eliminaciones accidentales
        verbose_name=_('Categoría'),
        default=1  # Se asegura que haya una categoría predeterminada
    )
    imagen = models.ImageField(_('Imagen'), upload_to='productos/', null=True, blank=True)
    descripcion = models.TextField(_('Descripción'), blank=True)
    creado = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    actualizado = models.DateTimeField(_('Última actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Producto')
        verbose_name_plural = _('Productos')
        ordering = ['-creado']
        indexes = [
            models.Index(fields=['nombre', 'marca']),
            models.Index(fields=['precio']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.marca}) - ${self.precio}"

    @property
    def disponible(self):
        """Indica si el producto está disponible y actualizado recientemente"""
        return self.stock > 0 and self.actualizado > timezone.now() - timedelta(days=30)

# Opciones predefinidas
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



class Cliente(models.Model):
    """Extensión del modelo User para datos adicionales del usuario"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')

    rut = models.CharField(
        _('RUT'),
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(regex=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', message=_('Formato: 12.345.678-9'))
        ]
    )

    telefono = models.CharField(
        _('Teléfono'),
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(regex=r'^\+?[0-9]{9,15}$', message=_('Formato: +56912345678'))
        ]
    )

    direccion = models.TextField(_('Dirección'), blank=True, max_length=300)
    comuna = models.CharField(_('Comuna'), max_length=100)

    nacionalidad = models.CharField(_('Nacionalidad'), max_length=20, choices=NACIONALIDADES)
    sexo = models.CharField(_('Sexo'), max_length=10, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField(_('Fecha de nacimiento'))

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username}"



class MensajeContacto(models.Model):
    """Modelo para mensajes recibidos del formulario de contacto"""
    nombre = models.CharField(_('Nombre completo'), max_length=100)
    email = models.EmailField(_('Email de contacto'))
    asunto = models.CharField(_('Asunto'), max_length=200)
    mensaje = models.TextField(_('Mensaje'))
    fecha = models.DateTimeField(_('Fecha de envío'), auto_now_add=True)
    leido = models.BooleanField(_('Leído'), default=False)

    class Meta:
        verbose_name = _('Mensaje de contacto')
        verbose_name_plural = _('Mensajes de contacto')
        ordering = ['-fecha', 'leido']

    def __str__(self):
        return f"Mensaje de {self.nombre} ({self.asunto})"

    @classmethod
    def marcar_todos_como_leidos(cls):
        """Marcar todos los mensajes como leídos de una sola vez"""
        cls.objects.filter(leido=False).update(leido=True)