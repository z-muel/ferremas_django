from .models import Producto

def carrito(request):
    carrito_items = []
    total = 0
    carrito = request.session.get('carrito', {})
    
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            subtotal = producto.precio * cantidad
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
        except Producto.DoesNotExist:
            continue
    
    return {
        'carrito_context': {
            'items': carrito_items,
            'total': total,
            'count': sum(carrito.values())
        }
    }