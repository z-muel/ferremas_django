from django.shortcuts import render, redirect
from django.contrib import messages  # Para mostrar mensajes al usuario
from .models import MensajeContacto, Producto

def inicio(request):
    return render(request, 'tienda/inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/productos.html', {'productos': productos})

def contacto(request):
    if request.method == 'POST':
        # Guarda el mensaje en la base de datos
        MensajeContacto.objects.create(
            nombre=request.POST.get('nombre'),
            email=request.POST.get('email'),
            asunto=request.POST.get('asunto'),
            mensaje=request.POST.get('mensaje')
        )
        messages.success(request, '¡Mensaje enviado correctamente!')  # Mensaje de confirmación
        return redirect('contacto')  # Recarga la página
    return render(request, 'tienda/contacto.html')

from rest_framework import generics
from .serializers import ProductoSerializer

class ProductoListAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer