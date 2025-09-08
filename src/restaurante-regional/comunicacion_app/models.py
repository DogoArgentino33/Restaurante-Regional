# src/comunicacion/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('nueva_reserva', 'Nueva reserva'),
        ('pedido_nuevo', 'Pedido nuevo'),
        ('reserva_cancelada', 'Reserva cancelada'),
        ('pedido_listo', 'Pedido listo'),
    ]
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    mensaje = models.TextField()
    modulo_origen = models.CharField(max_length=50, blank=True)
    referencia_id = models.IntegerField(null=True, blank=True)
    enviado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones_enviadas')
    enviado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones_recibidas')
    fecha_envio = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.get_tipo_display()} -> {self.enviado_a} - {self.fecha_envio}"


class Conversacion(models.Model):
    participantes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversaciones')
    creado_en = models.DateTimeField(auto_now_add=True)
    asunto = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'

    def __str__(self):
        return f"Conv {self.id} - {self.asunto or 'Sin asunto'}"


class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    enviado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='mensajes_enviados')
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['creado_en']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'

    def __str__(self):
        return f"Msg {self.id} - {self.enviado_por}"