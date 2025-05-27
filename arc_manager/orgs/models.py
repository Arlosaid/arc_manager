from django.db import models
from django.conf import settings

class Organization(models.Model):
    name = models.CharField("Nombre de la organización", max_length=200)
    slug = models.SlugField("Identificador único", unique=True, max_length=50)
    description = models.TextField("Descripción", blank=True, null=True)
    is_active = models.BooleanField("Activa", default=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    
    # Configuración básica
    max_users = models.PositiveIntegerField("Máximo de usuarios", default=10)
    
    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_user_count(self):
        return self.users.count()
    
    def can_add_user(self):
        return self.get_user_count() < self.max_users
    
    def get_admins(self):
        return self.users.filter(is_org_admin=True)
