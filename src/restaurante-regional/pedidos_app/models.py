# src/pedidos/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Pedido(models.Model):
    comensal = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    mesa = models.ForeignKey('reservas_app.Mesa', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    mozo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_atendidos')
    fecha = models.DateTimeField(default=timezone.now)
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_cocina', 'En cocina'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    total_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido {self.id} - {self.comensal.email}"

    def recalcular_total(self):
        total = sum([d.subtotal() for d in self.detalles.all()])
        self.total_estimado = total
        self.save(update_fields=['total_estimado'])
        return total


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('catalogo_app.Producto', on_delete=models.PROTECT, related_name='detalle_pedidos')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Detalle de pedido'
        verbose_name_plural = 'Detalles de pedido'

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} ({self.pedido.id})"


class AsignacionCocinero(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='asignaciones_cocinero')
    cocinero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_cocina')
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, default='en_preparacion')  # en_preparacion, finalizado, rechazado

    class Meta:
        ordering = ['-fecha_asignacion'] 
        verbose_name = 'Asignación de cocinero'
        verbose_name_plural = 'Asignaciones de cocinero'

    def __str__(self):
        return f"AsigCoc {self.id} - Pedido {self.pedido.id}"