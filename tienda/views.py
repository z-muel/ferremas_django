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
from .forms import ContactoForm, RegistroPersonalizadoForm  # ¡Crearemos estos forms después!

# Vistas principales
def inicio(request):
    """Vista para la página de inicio con productos destacados"""
    productos_destacados = Producto.objects.filter(stock__gt=0).order_by('-creado')[:4]
    return render(request, 'tienda/inicio.html', {
        'productos_destacados': productos_destacados
    })

def lista_productos(request):
    """Muestra todos los productos disponibles"""
    productos = Producto.objects.filter(stock__gt=0).select_related('categoria')
    return render(request, 'tienda/productos.html', {
        'productos': productos,
        'categorias': Categoria.objects.all()  # Para filtros
    })

# Autenticación y usuarios
def registro(request):
    """Vista para registro de nuevos usuarios"""
    if request.method == 'POST':
        form = RegistroPersonalizadoForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido/a')
            return redirect('inicio')
    else:
        form = RegistroPersonalizadoForm()
    
    return render(request, 'tienda/registro.html', {'form': form})

def login_view(request):
    """Vista personalizada para login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'inicio')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'tienda/login.html')

# Contacto y mensajes
def contacto(request):
    """Maneja el formulario de contacto"""
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensaje enviado. ¡Gracias por contactarnos!')
            return redirect('contacto')
    else:
        form = ContactoForm()
    
    return render(request, 'tienda/contacto.html', {'form': form})

# Carrito de compras
@require_POST
@login_required
def agregar_al_carrito(request, producto_id):
    """Añade un producto al carrito con validación de stock"""
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    
    if producto.stock <= 0:
        messages.error(request, 'Producto agotado')
        return redirect('productos')
    
    cantidad_actual = carrito.get(str(producto_id), 0)
    if cantidad_actual >= producto.stock:
        messages.warning(request, 'No hay suficiente stock')
        return redirect('productos')
    
    carrito[str(producto_id)] = cantidad_actual + 1
    request.session['carrito'] = carrito
    messages.success(request, f'{producto.nombre} añadido al carrito')
    return redirect('productos')

@login_required
def ver_carrito(request):
    """Muestra el contenido actual del carrito"""
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        subtotal = producto.precio * cantidad
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'tienda/carrito.html', {
        'items': items,
        'total': total
    })

# Pagos con Webpay
@login_required
def iniciar_pago(request):
    """Inicia el proceso de pago con Webpay"""
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('carrito')
    
    try:
        total = sum(
            Producto.objects.get(id=int(id)).precio * cantidad 
            for id, cantidad in carrito.items()
        )
        
        response = Transaction().create(
            buy_order=f"BO_{request.user.id}_{request.session.session_key[:8]}",
            session_id=request.session.session_key,
            amount=total,
            return_url=request.build_absolute_uri(reverse('pago_exitoso'))
        
        return redirect(response['url'])
    
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('carrito')

# API Banco Central
def convertir_moneda(request):
    """API para conversión de moneda usando datos del BC"""
    try:
        response = requests.get(
            "https://api.bcentral.cl/siete/uf",
            params={'apikey': 'TU_API_KEY'},
            timeout=5
        )
        response.raise_for_status()
        valor_uf = response.json()['uf']['valor']
        return JsonResponse({'valor_uf': valor_uf, 'status': 'success'})
    
    except requests.RequestException as e:
        return JsonResponse({'error': str(e), 'status': 'error'}, status=400)

# API REST
class ProductoListAPIView(generics.ListAPIView):
    """API para listado de productos"""
    queryset = Producto.objects.filter(stock__gt=0).select_related('categoria')
    serializer_class = ProductoSerializer
    pagination_class = None  # Temporal para desarrollo

class CategoriaListAPIView(generics.ListAPIView):
    """API para listado de categorías"""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer