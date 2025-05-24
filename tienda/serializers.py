from rest_framework import serializers
from .models import Producto, Categoria, MensajeContacto


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para categorías de productos"""
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador para productos de ferretería"""
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())  # Solo ID
    precio = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0)
    stock = serializers.IntegerField(min_value=0)
    disponible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'marca', 'modelo', 'precio', 'stock',
            'categoria', 'disponible', 'imagen', 'descripcion'
        ]

class ContactoSerializer(serializers.ModelSerializer):
    """Serializador para mensajes de contacto"""
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'asunto', 'mensaje', 'fecha', 'leido']
