from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from rest_framework import generics
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType
import requests    
from .models import MensajeContacto, Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer
from .forms import ProductoForm

# 🔹 Vistas principales
def inicio(request):
    productos_destacados = Producto.objects.filter(stock__gt=0)[:4]
    return render(request, 'tienda/inicio.html', {'productos_destacados': productos_destacados})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/productos.html', {'productos': productos})

# 🔹 Autenticación
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

# 🔹 Contacto
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

# 🔹 CRUD de Productos (Solo Administradores)
@login_required
def crear_producto(request):
    if not request.user.is_staff:  # ✅ Solo administradores pueden acceder
        raise PermissionDenied

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado exitosamente")
            return redirect('productos')
    else:
        form = ProductoForm()
    
    return render(request, 'tienda/crear_producto.html', {'form': form})

@login_required
def editar_producto(request, producto_id):
    if not request.user.is_staff:
        raise PermissionDenied

    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente")
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'tienda/editar_producto.html', {'form': form, 'producto': producto})

@login_required
def eliminar_producto(request, producto_id):
    if not request.user.is_staff:
        raise PermissionDenied

    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, "Producto eliminado exitosamente")
    return redirect('productos')

# 🔹 Carrito
@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})

    # ✅ Si el producto ya está en el carrito, aumenta la cantidad
    if str(producto_id) in carrito:
        carrito[str(producto_id)] += 1
    else:
        carrito[str(producto_id)] = 1

    request.session['carrito'] = carrito
    messages.success(request, f"{producto.nombre} agregado al carrito.")

    return redirect('ver_carrito')

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

@require_POST
def actualizar_carrito(request, producto_id):
    cantidad = int(request.POST.get('cantidad', 1))
    carrito = request.session.get('carrito', {})

    if cantidad > 0:
        carrito[str(producto_id)] = cantidad
    else:
        carrito.pop(str(producto_id), None)  # ✅ Si la cantidad es 0, elimina el producto

    request.session['carrito'] = carrito
    return redirect('ver_carrito')

@require_POST
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)  # ✅ Elimina el producto del carrito
    request.session['carrito'] = carrito
    messages.success(request, "Producto eliminado del carrito.")
    
    return redirect('ver_carrito')

# 🔹 Webpay 
def iniciar_pago(request):
    print("Iniciar pago ejecutándose...")  # ✅ Confirmación en consola
    carrito = request.session.get('carrito', {})
    total = sum(Producto.objects.get(id=int(pid)).precio * cantidad for pid, cantidad in carrito.items())

    buy_order = f"orden_{request.user.id}"
    session_id = request.session.session_key
    return_url = request.build_absolute_uri(reverse('confirmar_pago'))

    options = WebpayOptions(
        api_key="597020000541",
        commerce_code="597020000541",
        integration_type=IntegrationType.TEST
    )

    transaction = Transaction(options)

    try:
        response = transaction.create(buy_order, session_id, total, return_url)
        print(f"Respuesta completa de Webpay: {response}")  # ✅ Verifica la respuesta

        if 'url' in response:
            print(f"Redirigiendo a Webpay: {response['url']}")  # ✅ Confirmación en consola
            return redirect(response['url'])
        else:
            print("Error en Webpay: No se recibió una URL de pago válida.")  # ✅ Depuración extra
            messages.error(request, "Error en Webpay: No se recibió una URL de pago válida.")
            return redirect('ver_carrito')

    except Exception as e:
        print(f"Error en Webpay capturado: {e}")  # ✅ Imprimir el error exacto en consola
        messages.error(request, f"Error en Webpay: {e}")
        return redirect('ver_carrito')




def confirmar_pago(request):
    token = request.GET.get("token_ws", None)

    if not token:
        messages.error(request, "Error en la transacción.")
        return redirect('ver_carrito')

    transaction = Transaction(WebpayOptions(
        api_key="597020000541",
        commerce_code="597020000541",
        integration_type=IntegrationType.TEST
    ))

    response = transaction.commit(token)

    if response['status'] == 'AUTHORIZED':
        messages.success(request, "Pago realizado exitosamente.")
        request.session['carrito'] = {}  # ✅ Vaciar carrito tras compra
        return redirect('productos')
    else:
        messages.error(request, "El pago no pudo completarse.")
        return redirect('ver_carrito')


# 🔹 API Banco Central (optimizada)
def convertir_moneda(request):
    monto = float(request.GET.get('monto', 1))  # Monto base
    tasa = 890.75  # Simulación de tasa CLP/USD
    return JsonResponse({'monto_convertido': monto * tasa, 'tasa': tasa, 'status': 'success'})

# 🔹 API REST
class ProductoListAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class CategoriaListAPIView(generics.ListAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer