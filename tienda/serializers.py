from rest_framework import serializers
from .models import Producto, Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer()  # Serializador anidado para la categoría
    disponible = serializers.BooleanField(read_only=True)  # Campo calculado

    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'marca', 'modelo', 'precio', 'stock',
            'categoria', 'disponible', 'imagen', 'descripcion'
        ]