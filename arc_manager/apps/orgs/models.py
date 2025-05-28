from django.db import models
from django.conf import settings
from apps.plans.models import Plan

class Organization(models.Model):
    name = models.CharField("Nombre de la organización", max_length=200)
    slug = models.SlugField("Identificador único", unique=True, max_length=50)
    description = models.TextField("Descripción", blank=True, null=True)
    is_active = models.BooleanField("Activa", default=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    
    # Plan de la organización
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, verbose_name="Plan", null=True, blank=True)
    
    # Configuración básica - DEPRECATED: mantener por compatibilidad
    max_users = models.PositiveIntegerField("Máximo de usuarios", default=1, 
                                          help_text="DEPRECATED: Usar el plan en su lugar")
    
    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Override save para asegurar que siempre haya un plan asignado"""
        if not self.plan_id:
            # Si no hay plan asignado, asignar el plan gratuito por defecto
            try:
                default_plan = Plan.objects.get(name='gratuito')
                self.plan = default_plan
            except Plan.DoesNotExist:
                pass
        
        # Sincronizar max_users con el plan asignado
        if self.plan:
            self.max_users = self.plan.max_users
        
        super().save(*args, **kwargs)
    
    def get_max_users(self):
        """Retorna el límite de usuarios basado en el plan"""
        if self.plan:
            return self.plan.max_users
        # Fallback al campo max_users si no hay plan asignado
        return self.max_users
    
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
        return self.get_user_count() < self.get_max_users()
    
    def can_add_user_detailed(self):
        """
        Retorna información detallada sobre si se puede agregar un usuario
        Returns: dict con información del estado
        """
        active_count = self.get_active_user_count()
        inactive_count = self.get_inactive_user_count()
        total_count = self.get_user_count()
        max_users = self.get_max_users()
        
        return {
            'can_add': total_count < max_users,
            'active_users': active_count,
            'inactive_users': inactive_count,
            'total_users': total_count,
            'max_users': max_users,
            'available_slots': max(0, max_users - total_count),
            'is_at_limit': total_count >= max_users,
            'has_inactive_users': inactive_count > 0
        }
    
    def get_admins(self):
        return self.users.filter(is_org_admin=True)
