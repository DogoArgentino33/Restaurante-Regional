from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # 'efectivo', 'debito', 'credito', 'QR'
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Método de pago'
        verbose_name_plural = 'Métodos de pago'

    def str(self):
        return self.nombre


class Factura(models.Model):
    pedido = models.OneToOneField('pedidos.Pedido', on_delete=models.CASCADE, related_name='factura')
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, related_name='facturas')
    fecha = models.DateTimeField(default=timezone.now)
    generado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='facturas_generadas')
    datos_extra = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def str(self):
        return f"Factura {self.id} - Pedido {self.pedido.id} - ${self.total}"