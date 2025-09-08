from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# Create your models here.

class PersonaManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        return self.create_user(email, password, **extra_fields)


class Persona(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    apellido = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    objects = PersonaManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        if self.nombre or self.apellido:
            return f"{self.nombre} {self.apellido} <{self.email}>"
        return self.email

    @property
    def full_name(self):
        return f"{self.nombre} {self.apellido}".strip()


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # e.g. 'Comensal', 'Mozo', 'Cocinero', 'Gerente', 'Admin'
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class PersonaRol(models.Model):
    persona = models.ForeignKey('gestion.Persona', on_delete=models.CASCADE, related_name='persona_roles')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='persona_roles')
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('persona', 'rol')
        verbose_name = 'AsignaciÃ³n de rol'
        verbose_name_plural = 'Asignaciones de rol'

    def __str__(self):
        return f"{self.persona.email} => {self.rol.nombre}"