from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Categoría de producto'
        verbose_name_plural = 'Categorías de producto'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)[:60]
        super().save(*args, **kwargs)


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    disponible = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='productos/%Y/%m', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        indexes = [models.Index(fields=['nombre']), models.Index(fields=['slug'])]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)[:115]
            slug = base
            if Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{int(timezone.now().timestamp())}"
            self.slug = slug[:120]
        super().save(*args, **kwargs)


class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    cantidad = models.IntegerField(default=0)
    unidad = models.CharField(max_length=20, default='u')  # ej. 'kg', 'u', 'lts'
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'

    def __str__(self):
        return f"{self.producto.nombre}: {self.cantidad} {self.unidad}"

    def ajustar_stock(self, delta, motivo='', user=None):
        anterior = self.cantidad
        nueva = anterior + int(delta)
        self.cantidad = nueva
        self.save()
        MovimientoInventario.objects.create(
            producto=self.producto,
            cantidad_anterior=anterior,
            cantidad_cambio=int(delta),
            cantidad_nueva=nueva,
            motivo=motivo or ('ajuste' if delta != 0 else 'sin_cambio'),
            realizado_por=user
        )
        return self.cantidad


class MovimientoInventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    cantidad_anterior = models.IntegerField()
    cantidad_cambio = models.IntegerField()  # positivo o negativo
    cantidad_nueva = models.IntegerField()
    motivo = models.CharField(max_length=100)  # 'uso en pedido','ajuste','compra'
    realizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_inventario')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'

    def __str__(self):
        sign = '+' if self.cantidad_cambio >= 0 else ''
        return f"{self.producto.nombre}: {sign}{self.cantidad_cambio} -> {self.cantidad_nueva} ({self.motivo})"


class MenuDia(models.Model):
    fecha = models.DateField(unique=True)
    productos = models.ManyToManyField(Producto, related_name='menu_dias', blank=True)
    nota = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Menú del día'
        verbose_name_plural = 'Menús del día'

    def __str__(self):
        return f"Menú {self.fecha}"


class Calificacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='calificaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='calificaciones')
    puntaje = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        # unique_together = ('producto','usuario')  # opcional

    def __str__(self):
        return f"{self.puntaje} - {self.producto.nombre} ({self.usuario})"