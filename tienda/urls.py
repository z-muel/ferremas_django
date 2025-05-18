from django.urls import path
from . import views
from .views import ProductoListAPIView  

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='productos'),
    path('contacto/', views.contacto, name='contacto'),
    path('api/productos/', ProductoListAPIView.as_view(), name='api_productos'),  # Ruta API
]