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
    convertir_moneda,
    ProductoListAPIView,
    CategoriaListAPIView  
)

urlpatterns = [
    path('', inicio, name='inicio'),
    path('productos/', lista_productos, name='productos'),
    path('contacto/', contacto, name='contacto'),
    path('registro/', registro, name='registro'),
    path('login/', login_view, name='login'),
    path('agregar-carrito/<int:producto_id>/', agregar_al_carrito, name='agregar_carrito'),
    path('carrito/', ver_carrito, name='carrito'),
    path('api/productos/', ProductoListAPIView.as_view(), name='api_productos'),
    path('api/categorias/', CategoriaListAPIView.as_view(), name='api_categorias'),
    path('api/tipo-cambio/', convertir_moneda, name='api_tipo_cambio'),
    path('iniciar-pago/', views.iniciar_pago, name='iniciar_pago'),
]