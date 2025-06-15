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
from django.views.decorators.csrf import csrf_exempt
from .forms import RegistroCompletoForm
import os




# Vistas principales
def inicio(request):
    productos_destacados = Producto.objects.filter(stock__gt=0)[:4]
    return render(request, 'tienda/inicio.html', {'productos_destacados': productos_destacados})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/productos.html', {'productos': productos})

# Autenticación
def registro(request):
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registro exitoso. ¡Bienvenido!")
            return redirect('inicio')
        else:
            messages.error(request, "Error en el registro. Revisa los datos ingresados.")
    else:
        form = RegistroCompletoForm()
    
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

# CRUD de Productos (Solo Administradores)
@login_required
def crear_producto(request):
    if not request.user.is_staff:  # Solo administradores pueden acceder
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

# Carrito
@csrf_exempt  # Desactiva CSRF solo para pruebas.

@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        carrito[str(producto_id)] += 1
    else:
        carrito[str(producto_id)] = 1

    request.session['carrito'] = carrito
    request.session.modified = True

    # Si la solicitud viene de Postman (API), devolver JSON correctamente
    if request.headers.get('Accept') == 'application/json' or request.GET.get('api') == 'true':
        return JsonResponse({"mensaje": f"{producto.nombre} agregado al carrito.", "status": "success"})

    # Si la solicitud es desde el navegador, redirigir al carrito
    messages.success(request, f"{producto.nombre} agregado al carrito.")
    return redirect(reverse('ver_carrito'))



def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.filter(id=int(producto_id)).first()
        if producto:
            subtotal = producto.precio * cantidad
            productos.append({
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': producto.precio,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal

    # Si la solicitud viene de Postman o es una API, devolver JSON
    if request.headers.get('Accept') == 'application/json' or request.GET.get('api') == 'true':
        return JsonResponse({'productos': productos, 'total': total})

    return render(request, 'tienda/carrito.html', {'productos': productos, 'total': total})


@require_POST
def actualizar_carrito(request, producto_id):
    cantidad = int(request.POST.get('cantidad', 1))
    carrito = request.session.get('carrito', {})

    if cantidad > 0:
        carrito[str(producto_id)] = cantidad
    else:
        carrito.pop(str(producto_id), None)  # Si la cantidad es 0, elimina el producto

    request.session['carrito'] = carrito
    return redirect('ver_carrito')

@csrf_exempt  # Desactiva CSRF solo para pruebas

@require_POST
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)  # Elimina el producto del carrito
    request.session['carrito'] = carrito
    messages.success(request, "Producto eliminado del carrito.")
    
    return redirect('ver_carrito')

# Webpay 
def iniciar_pago(request):
    print("Iniciar pago ejecutándose...")  # Depuración en consola
    carrito = request.session.get('carrito', {})
    total = sum(Producto.objects.get(id=int(pid)).precio * cantidad for pid, cantidad in carrito.items())

    buy_order = f"ORD-{request.session.session_key}"[:26]  
    session_id = request.session.session_key or "SESSION1234"
    return_url = request.build_absolute_uri(reverse('webpay_confirmacion')) 

    # credenciales de prueba
    options = WebpayOptions(
    api_key=os.getenv("WEBPAY_API_KEY"),
    commerce_code=os.getenv("WEBPAY_COMMERCE_CODE"),
    integration_type=IntegrationType.TEST
)


    transaction = Transaction(options)

    
    try:
        response = transaction.create(buy_order, session_id, total, return_url)
        print(f"Respuesta completa de Webpay: {response}")  # Depuración en consola

        if 'url' in response and 'token' in response:
            return redirect(f"{response['url']}?token_ws={response['token']}")
        else:
            messages.error(request, "❌ Error en Webpay: No se recibió una URL de pago válida.")
            return redirect('pago_fallido')  # Redirigir a la pantalla de fallo en lugar del carrito

    except Exception as e:
        print(f"⚠ Error en Webpay capturado: {e}")
        messages.error(request, f"Error técnico en Webpay: {e}")
        return redirect('pago_fallido')  # Mostrar detalles del error en la pantalla de fallo


def confirmar_pago(request):
    token_ws = request.GET.get("token_ws")
    tbk_token = request.GET.get("TBK_TOKEN")  # 🔍 Detectamos TBK_TOKEN cuando la compra es anulada

    print(f"🔍 Token recibido: {token_ws}")  # Depuración
    print(f"🔍 TBK_TOKEN recibido: {tbk_token}")  # Depuración

    if tbk_token:  # 🚨 Si Webpay devuelve TBK_TOKEN, significa que el usuario anuló la compra
        messages.info(request, "❌ Has cancelado la compra. No se ha realizado ningún cargo.")
        return redirect('pago_cancelado')

    if not token_ws:  # ❌ Si no hay token_ws, hubo un error en la transacción
        messages.error(request, "❌ Error en la transacción: Token no recibido.")
        return redirect('pago_fallido')

    # 🔒 Usar credenciales desde variables de entorno
    options = WebpayOptions(
        api_key=os.getenv("WEBPAY_API_KEY"),
        commerce_code=os.getenv("WEBPAY_COMMERCE_CODE"),
        integration_type=IntegrationType.TEST
    )
    transaction = Transaction(options)

    try:
        response = transaction.commit(token_ws)
        print("✅ Respuesta de Webpay:", response)  # Depuración

        if response.get('status') == 'AUTHORIZED':
            messages.success(request, "✅ Pago realizado exitosamente.")

            # 🔥 Vaciar la sesión completamente para eliminar el carrito
            request.session.flush()

            # 🚀 Pasar más detalles del pago a la plantilla
            return render(request, 'tienda/pago_exitoso.html', {
                'buy_order': response.get('buy_order'),
                'amount': response.get('amount'),
                'authorization_code': response.get('authorization_code'),
                'transaction_date': response.get('transaction_date'),
                'detalle_pago': response
            })

        else:
            messages.error(request, "❌ El pago fue rechazado o no pudo completarse.")
            return render(request, 'tienda/pago_fallido.html', {
                'detalle_pago': response,
                'error_message': response.get('response_code', 'Error desconocido')
            })

    except Exception as e:
        print(f"⚠ Error en Webpay al confirmar pago: {e}")
        messages.error(request, f"Error en Webpay: {e}")
        return render(request, 'tienda/pago_fallido.html', {
            'error_message': str(e)
        })

# ✅ Rutas para pantallas de éxito y fallo
def pago_exitoso(request):
    return render(request, 'tienda/pago_exitoso.html')

def pago_fallido(request):
    return render(request, 'tienda/pago_fallido.html')

# Pantalla de cancelación de pago

def pago_cancelado(request):
    messages.info(request, "❌ Has cancelado la compra. No se ha realizado ningún cargo.")
    return render(request, 'tienda/pago_cancelado.html', {'mensaje_cancelado': "Has cancelado tu compra. No se ha realizado ningún cobro."})



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