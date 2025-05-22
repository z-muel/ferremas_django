from django.urls import path
from . import views
from .views import (
    inicio,
    lista_productos,
    contacto,
    registro,
    login_view,
    agregar_al_carrito,
    ver_carrito,
    ProductoListAPIView,
    CategoriaListAPIView,
    iniciar_pago,
)

# Importa las vistas de API que creamos anteriormente
from .api import (
    ContactoCreateAPIView,
    MonedaAPIView,
    WebpayAPIView,
)

urlpatterns = [
    # URLs de vistas HTML (frontend)
    path('', inicio, name='inicio'),
    path('productos/', lista_productos, name='productos'),
    path('contacto/', contacto, name='contacto'),
    path('registro/', registro, name='registro'),
    path('login/', login_view, name='login'),
    path('agregar-carrito/<int:producto_id>/', agregar_al_carrito, name='agregar_carrito'),
    path('carrito/', ver_carrito, name='carrito'),
    path('iniciar-pago/', iniciar_pago, name='iniciar_pago'),

    # URLs de APIs (REST)
    path('api/productos/', ProductoListAPIView.as_view(), name='api_productos'),
    path('api/categorias/', CategoriaListAPIView.as_view(), name='api_categorias'),
    path('api/contacto/', ContactoCreateAPIView.as_view(), name='api_contacto'),
    path('api/moneda/', MonedaAPIView.as_view(), name='api_moneda'),
    path('api/webpay/', WebpayAPIView.as_view(), name='api_webpay'),
]