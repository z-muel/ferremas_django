from django.urls import path, include
from tienda import views

urlpatterns = [
    # URLs del sitio (frontend)
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('contacto/', views.contacto, name='contacto'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    
    # Carrito de compras
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),  
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),  
    
    # Pago
    path("webpay/pagar/", views.iniciar_pago, name="webpay_pagar"),
    path("webpay/confirmacion/", views.confirmar_pago, name="webpay_confirmacion"),

    

    # APIs separadas
    path('api/', include('tienda.urls_api')),
]