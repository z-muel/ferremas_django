from rest_framework import generics, status
from rest_framework.response import Response
from .models import Producto, MensajeContacto
from .serializers import ProductoSerializer, ContactoSerializer
import random

# Vista para listar productos
class ProductoListAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

# Vista para enviar mensajes de contacto
class ContactoCreateAPIView(generics.CreateAPIView):
    queryset = MensajeContacto.objects.all()
    serializer_class = ContactoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"mensaje": "Gracias por tu mensaje. Te responderemos pronto."},
            status=status.HTTP_201_CREATED
        )

# Vista para conversión de moneda (simulada)
class MonedaAPIView(generics.GenericAPIView):
    def get(self, request):
        clp = float(request.query_params.get('clp', 0))
        tasa_usd = 950  # Tasa simulada: 1 USD = 950 CLP
        valor_usd = clp / tasa_usd
        return Response({"valor_usd": round(valor_usd, 2)})

# Vista para Webpay simulado
class WebpayAPIView(generics.GenericAPIView):
    def post(self, request):
        monto = request.data.get('monto')
        return Response({
            "status": "success",
            "transaction_id": random.randint(100000, 999999),
            "monto": monto,
            "message": "Pago simulado exitosamente (Webpay)"
        })