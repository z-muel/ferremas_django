from django.contrib import admin
from .models import Categoria, Producto, Cliente, MensajeContacto

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'marca', 'precio', 'stock')
    search_fields = ('codigo', 'nombre', 'marca')
    list_filter = ('categoria', 'marca')

admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente)
admin.site.register(MensajeContacto)