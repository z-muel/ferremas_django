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
    productos_destacados = Producto.objects.filter(stock__gt=0)[:4]
    return render(request, 'tienda/inicio.html', {'productos_destacados': productos_destacados})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/productos.html', {'productos': productos})

# Autenticación
def registro(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Registro exitoso. Bienvenido!")
        return redirect('inicio')
    
    return render(request, 'tienda/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect('inicio')
        else:
            messages.error(request, "Credenciales incorrectas.")
    
    return render(request, 'tienda/login.html')

# Contacto
def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        asunto = request.POST.get('asunto', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        
        if not nombre or not email or not asunto or not mensaje:
            messages.error(request, 'Todos los campos son obligatorios')
        else:
            MensajeContacto.objects.create(
                nombre=nombre, email=email, asunto=asunto, mensaje=mensaje
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
        producto = Producto.objects.filter(id=int(producto_id)).first()
        if producto:
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

# Webpay (versión mejorada)
def iniciar_pago(request):
    carrito = request.session.get('carrito', {})
    total = 0
    
    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.filter(id=int(producto_id)).first()
        if producto:
            total += producto.precio * cantidad
    
    response = Transaction().create(
        buy_order=f"orden_{request.user.id}",
        session_id=request.session.session_key,
        amount=total,
        return_url=request.build_absolute_uri(reverse('inicio'))
    )
    
    return redirect(response['url'])

# API Banco Central (optimizada)
def convertir_moneda(request):
    monto = float(request.GET.get('monto', 1))  # Monto base
    tasa = 890.75  # Simulación de tasa CLP/USD
    return JsonResponse({'monto_convertido': monto * tasa, 'tasa': tasa, 'status': 'success'})

# API REST
class ProductoListAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class CategoriaListAPIView(generics.ListAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer