from django.db import models
from django.conf import settings

class Organization(models.Model):
    name = models.CharField("Nombre de la organización", max_length=200)
    slug = models.SlugField("Identificador único", unique=True, max_length=50)
    description = models.TextField("Descripción", blank=True, null=True)
    is_active = models.BooleanField("Activa", default=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    
    # Configuración básica - UN SOLO LÍMITE PARA TODOS
    max_users = models.PositiveIntegerField("Máximo de usuarios", default=10, 
                                          help_text="Límite total de usuarios (activos e inactivos)")
    
    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_user_count(self):
        """Retorna el total de usuarios (activos e inactivos)"""
        return self.users.count()
    
    def get_active_user_count(self):
        """Retorna solo el número de usuarios activos"""
        return self.users.filter(is_active=True).count()
    
    def get_inactive_user_count(self):
        """Retorna solo el número de usuarios inactivos"""
        return self.users.filter(is_active=False).count()
    
    def can_add_user(self):
        """Verifica si se puede agregar cualquier usuario (activo o inactivo)"""
        return self.get_user_count() < self.max_users
    
    def can_add_user_detailed(self):
        """
        Retorna información detallada sobre si se puede agregar un usuario
        Returns: dict con información del estado
        """
        active_count = self.get_active_user_count()
        inactive_count = self.get_inactive_user_count()
        total_count = self.get_user_count()
        
        return {
            'can_add': total_count < self.max_users,
            'active_users': active_count,
            'inactive_users': inactive_count,
            'total_users': total_count,
            'max_users': self.max_users,
            'available_slots': max(0, self.max_users - total_count),
            'is_at_limit': total_count >= self.max_users,
            'has_inactive_users': inactive_count > 0
        }
    
    def get_admins(self):
        return self.users.filter(is_org_admin=True)
