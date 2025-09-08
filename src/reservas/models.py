from django.db import models
from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField(default=4)
    ubicacion = models.CharField(max_length=50, blank=True)
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('ocupada', 'Ocupada'),
        ('fuera_servicio', 'Fuera de servicio'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['numero']
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'

    def __str__(self):
        return f"Mesa {self.numero} (cap. {self.capacidad})"

    def marcar_reservada(self):
        self.estado = 'reservada'
        self.save(update_fields=['estado'])


class Reserva(models.Model):
    comensal = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservas')
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name='reservas')
    fecha = models.DateTimeField()
    cantidad_personas = models.PositiveIntegerField(default=1)
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('en_espera', 'En espera'),
        ('atendida', 'Atendida'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"Reserva {self.id} - {self.comensal.email} - {self.fecha}"

    def is_conflict(self):
        """
        Comprueba si hay otra reserva confirmada para la misma mesa en el mismo rango horario.
        Implementación básica: consulta reservas confirmadas con la misma fecha exacta.
        Ajustar según ventana de tiempo (ej. +/- 2 horas) si se necesita.
        """
        return Reserva.objects.filter(
            mesa=self.mesa,
            fecha=self.fecha,
            estado__in=['confirmada', 'pendiente']
        ).exclude(pk=self.pk).exists()


class AsignacionMesa(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='asignaciones_mesa')
    mozo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='asignaciones_mesa')
    fecha_asignacion = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fecha_asignacion']
        verbose_name = 'Asignación de mesa'
        verbose_name_plural = 'Asignaciones de mesa'

    def __str__(self):
        return f"AsigMesa {self.id} - Reserva {self.reserva.id}"