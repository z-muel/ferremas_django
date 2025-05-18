from django.shortcuts import render
from .models import Producto

def inicio(request):
    return render(request, 'tienda/inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/productos.html', {'productos': productos})

def contacto(request):
    if request.method == 'POST':
        # Lógica para procesar formulario
        pass
    return render(request, 'tienda/contacto.html')