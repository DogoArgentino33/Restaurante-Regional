from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class AuditoriaReserva(models.Model):
    reserva = models.ForeignKey('reservas.Reserva', on_delete=models.CASCADE, related_name='auditorias')
    accion = models.CharField(max_length=50)  # creada, modificada, cancelada, confirmada
    realizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='auditorias_reserva')
    fecha = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Auditoría de reserva'
        verbose_name_plural = 'Auditorías de reserva'

    def __str__(self):
        return f"AudRes {self.id} - {self.accion}"


class AuditoriaPedido(models.Model):
    pedido = models.ForeignKey('pedidos.Pedido', on_delete=models.CASCADE, related_name='auditorias')
    accion = models.CharField(max_length=50)  # creado, enviado_a_cocina, entregado
    realizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='auditorias_pedido')
    fecha = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Auditoría de pedido'
        verbose_name_plural = 'Auditorías de pedido'

    def __str__(self):
        return f"AudPed {self.id} - {self.accion}"


class AuditoriaInventario(models.Model):
    producto = models.ForeignKey('catalogo.Producto', on_delete=models.CASCADE, related_name='auditorias_inventario')
    cantidad_anterior = models.IntegerField()
    cantidad_nueva = models.IntegerField()
    motivo = models.CharField(max_length=100)  # uso en pedido, ajuste, compra
    realizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='auditorias_inventario')
    fecha = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Auditoría de inventario'
        verbose_name_plural = 'Auditorías de inventario'

    def __str__(self):
        return f"AudInv {self.id} - {self.producto.nombre}"