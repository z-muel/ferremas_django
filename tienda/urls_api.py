from django.urls import path
from .api import ContactoCreateAPIView, MonedaAPIView, WebpayAPIView
from .views import ProductoListAPIView, CategoriaListAPIView


urlpatterns = [
    path('productos/', ProductoListAPIView.as_view(), name='api_productos'),
    path('categorias/', CategoriaListAPIView.as_view(), name='api_categorias'),
    path('contacto/', ContactoCreateAPIView.as_view(), name='api_contacto'),
    path('moneda/', MonedaAPIView.as_view(), name='api_moneda'),
    path('webpay/', WebpayAPIView.as_view(), name='api_webpay'),
   
]