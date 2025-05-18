from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

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
    nombre = models.CharField(
        _('Nombre'),
        max_length=200,
        help_text=_('Nombre completo del producto')
    )
    marca = models.CharField(
        _('Marca'),
        max_length=100
    )
    modelo = models.CharField(
        _('Modelo'),
        max_length=100
    )
    precio = models.DecimalField(
        _('Precio'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(
        _('Stock disponible'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Categoría')
    )
    imagen = models.ImageField(
        _('Imagen'),
        upload_to='productos/',
        null=True,
        blank=True,
        help_text=_('Imagen del producto (500x500px recomendado)')
    )
    descripcion = models.TextField(
        _('Descripción'),
        blank=True
    )
    creado = models.DateTimeField(
        _('Fecha de creación'),
        auto_now_add=True
    )
    actualizado = models.DateTimeField(
        _('Última actualización'),
        auto_now=True
    )

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
        """Indica si el producto está disponible para venta"""
        return self.stock > 0


class Cliente(models.Model):
    """Extensión del modelo User para información adicional"""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cliente'
    )
    telefono = models.CharField(
        _('Teléfono'),
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex='^\+?[0-9]{9,15}$',
                message=_('Formato: +56912345678')
            )
        ]
    )
    direccion = models.TextField(
        _('Dirección'),
        blank=True,
        max_length=300
    )

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username}"


class MensajeContacto(models.Model):
    """Modelo para mensajes recibidos del formulario de contacto"""
    nombre = models.CharField(
        _('Nombre completo'),
        max_length=100
    )
    email = models.EmailField(
        _('Email de contacto')
    )
    asunto = models.CharField(
        _('Asunto'),
        max_length=200
    )
    mensaje = models.TextField(
        _('Mensaje')
    )
    fecha = models.DateTimeField(
        _('Fecha de envío'),
        auto_now_add=True
    )
    leido = models.BooleanField(
        _('Leído'),
        default=False
    )

    class Meta:
        verbose_name = _('Mensaje de contacto')
        verbose_name_plural = _('Mensajes de contacto')
        ordering = ['-fecha', 'leido']

    def __str__(self):
        return f"Mensaje de {self.nombre} ({self.asunto})"

    def marcar_como_leido(self):
        self.leido = True
        self.save(update_fields=['leido'])