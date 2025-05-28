from django.db import models

# Create your models here.

class Plan(models.Model):
    """Modelo para definir planes de la aplicación"""
    PLAN_TYPES = [
        ('gratuito', 'Gratuito'),
        ('basico', 'Básico'),
    ]
    
    name = models.CharField("Nombre del plan", max_length=50, choices=PLAN_TYPES, unique=True)
    display_name = models.CharField("Nombre para mostrar", max_length=100)
    description = models.TextField("Descripción", blank=True)
    max_users = models.PositiveIntegerField("Máximo de usuarios")
    price = models.DecimalField("Precio mensual", max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    
    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ['price', 'max_users']
    
    def __str__(self):
        return self.display_name
