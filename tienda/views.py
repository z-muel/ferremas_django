from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from transbank.webpay.webpay_plus.transaction import Transaction
import requests
from .models import MensajeContacto, Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer

# Vistas principales
def inicio(request):
    productos = Producto.objects.filter(stock__gt=0)[:4]
    return render(request, 'tienda/inicio.html', {'productos': productos})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/productos.html', {'productos': productos})

# Autenticación
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = UserCreationForm()
    return render(request, 'tienda/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
    return render(request, 'tienda/login.html')

# Contacto
def contacto(request):
    if request.method == 'POST':
        MensajeContacto.objects.create(
            nombre=request.POST.get('nombre'),
            email=request.POST.get('email'),
            asunto=request.POST.get('asunto'),
            mensaje=request.POST.get('mensaje')
        )
        messages.success(request, 'Mensaje enviado!')
        return redirect('contacto')
    return render(request, 'tienda/contacto.html')

# Carrito
@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    carrito[str(producto_id)] = carrito.get(str(producto_id), 0) + 1
    request.session['carrito'] = carrito
    return redirect('productos')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        subtotal = producto.precio * cantidad
        productos.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'tienda/carrito.html', {
        'productos': productos,
        'total': total
    })

# Webpay (versión simplificada)
def iniciar_pago(request):
    carrito = request.session.get('carrito', {})
    total = sum(
        Producto.objects.get(id=int(id)).precio * cantidad 
        for id, cantidad in carrito.items()
    )
    
    response = Transaction().create(
        buy_order="orden_"+str(request.user.id),
        session_id=request.session.session_key,
        amount=total,
        return_url=request.build_absolute_uri(reverse('inicio'))
    )
    return redirect(response['url'])

# API Banco Central (simulada)
def convertir_moneda(request):
    # Datos de ejemplo para la evaluación
    return JsonResponse({'valor': 35000, 'status': 'success'})

# API REST
class ProductoListAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class CategoriaListAPIView(generics.ListAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer