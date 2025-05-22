from django.urls import path, include
from . import views

urlpatterns = [
    # URLs del sitio (frontend)
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='productos'),
    path('contacto/', views.contacto, name='contacto'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('iniciar-pago/', views.iniciar_pago, name='iniciar_pago'),

    # APIs separadas
    path('api/', include('tienda.urls_api')),
]