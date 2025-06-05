# apps/orgs/models.py - Versión simplificada
from django.db import models
from django.utils import timezone

class Organization(models.Model):
    """Modelo simplificado de organización"""
    
    name = models.CharField("Nombre de la organización", max_length=200)
    slug = models.SlugField("Identificador único", unique=True, max_length=50)
    description = models.TextField("Descripción", blank=True, null=True)
    is_active = models.BooleanField("Activa", default=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_subscription(self):
        """Retorna la suscripción actual de la organización"""
        try:
            return self.subscription
        except:
            # Si no tiene suscripción, crear trial por defecto
            return self._create_default_subscription()
    
    def _create_default_subscription(self):
        """Crea suscripción trial por defecto para nuevas organizaciones"""
        from apps.plans.models import Plan, Subscription
        
        try:
            trial_plan = Plan.objects.get(name='trial', is_active=True)
            subscription = Subscription.objects.create(
                organization=self,
                plan=trial_plan
            )
            return subscription
        except Plan.DoesNotExist:
            return None
    
    def get_max_users(self):
        """Retorna el límite de usuarios basado en el plan"""
        subscription = self.get_subscription()
        return subscription.plan.max_users if subscription else 1
    
    def get_user_count(self):
        """Retorna el total de usuarios"""
        return self.users.count()
    
    def get_active_user_count(self):
        """Retorna solo usuarios activos"""
        return self.users.filter(is_active=True).count()
    
    def get_inactive_user_count(self):
        """Retorna usuarios inactivos"""
        return self.users.filter(is_active=False).count()
    
    def can_add_user(self):
        """Verifica si se puede agregar un usuario"""
        return self.get_user_count() < self.get_max_users()
    
    def can_add_user_detailed(self):
        """Información detallada sobre capacidad de usuarios"""
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
    
    def is_trial(self):
        """Verifica si está en período de trial"""
        subscription = self.get_subscription()
        return subscription and subscription.plan.is_trial and subscription.is_active()
    
    def trial_days_remaining(self):
        """Días restantes de trial"""
        subscription = self.get_subscription()
        if subscription and subscription.plan.is_trial:
            return subscription.days_remaining()
        return 0
    
    def get_admins(self):
        """Retorna usuarios administradores"""
        return self.users.filter(is_org_admin=True)
    
    @property
    def plan(self):
        """Retorna el plan actual de la organización"""
        subscription = self.get_subscription()
        return subscription.plan if subscription else None
    
    def get_subscription_status(self):
        """Retorna el estado de la suscripción"""
        if hasattr(self, 'subscription'):
            return self.subscription.status
        return 'no_subscription'
    
    def is_subscription_active(self):
        """Verifica si la suscripción está activa"""
        if hasattr(self, 'subscription'):
            return self.subscription.is_active
        return False
    
    def get_current_plan(self):
        """Retorna el plan actual de la organización"""
        if hasattr(self, 'subscription'):
            return self.subscription.plan
        return None
    
    def can_create_user_with_subscription(self):
        """Verifica si puede crear usuarios considerando la suscripción"""
        if not self.is_subscription_active():
            return {
                'can_create': False,
                'reason': 'Suscripción inactiva o expirada',
                'subscription_required': True
            }
        
        current_plan = self.get_current_plan()
        if not current_plan:
            return {
                'can_create': False,
                'reason': 'No hay plan asignado',
                'subscription_required': True
            }
        
        current_count = self.get_user_count()
        can_create = current_count < current_plan.max_users
        
        return {
            'can_create': can_create,
            'reason': 'Límite de usuarios alcanzado' if not can_create else 'OK',
            'current_count': current_count,
            'limit': current_plan.max_users,
            'subscription_required': False
        }
    
    def get_subscription_limits(self):
        """Retorna todos los límites de la suscripción actual"""
        if not hasattr(self, 'subscription') or not self.subscription.is_active:
            return {
                'users': {'current': 0, 'limit': 0, 'available': 0},
                'projects': {'current': 0, 'limit': 0, 'available': 0},
                'storage_gb': {'current': 0, 'limit': 0, 'available': 0},
                'subscription_active': False
            }
        
        plan = self.subscription.plan
        user_count = self.get_user_count()
        
        # TODO: Implementar cuando tengas los módulos de proyectos y almacenamiento
        project_count = 0  # self.projects.count() when implemented
        storage_used = 0   # self.get_storage_usage() when implemented
        
        return {
            'users': {
                'current': user_count,
                'limit': plan.max_users,
                'available': max(0, plan.max_users - user_count),
                'usage_percentage': plan.get_usage_percentage(user_count, 'users')
            },
            'projects': {
                'current': project_count,
                'limit': plan.max_projects,
                'available': max(0, plan.max_projects - project_count),
                'usage_percentage': plan.get_usage_percentage(project_count, 'projects')
            },
            'storage_gb': {
                'current': storage_used,
                'limit': plan.storage_limit_gb,
                'available': max(0, plan.storage_limit_gb - storage_used),
                'usage_percentage': plan.get_usage_percentage(storage_used, 'storage_gb')
            },
            'subscription_active': True
        }
    
    def get_subscription_warning_level(self):
        """Retorna el nivel de advertencia de la suscripción"""
        if not hasattr(self, 'subscription'):
            return 'error'  # No subscription
        
        subscription = self.subscription
        
        if not subscription.is_active:
            return 'error'  # Inactive subscription
        
        days_remaining = subscription.days_remaining
        
        if days_remaining <= 3:
            return 'critical'  # Critical - expires in 3 days or less
        elif days_remaining <= 7:
            return 'warning'   # Warning - expires in 7 days or less
        elif days_remaining <= 14:
            return 'info'      # Info - expires in 14 days or less
        else:
            return 'success'   # All good
    
    def get_next_billing_info(self):
        """Retorna información de la próxima facturación"""
        if not hasattr(self, 'subscription'):
            return None
        
        subscription = self.subscription
        plan = subscription.plan
        
        return {
            'next_billing_date': subscription.next_billing_date,
            'amount': plan.price,
            'currency': plan.currency,
            'billing_cycle': plan.get_billing_cycle_display(),
            'days_until_billing': subscription.days_remaining,
            'auto_renew': subscription.auto_renew
        }
    
    def calculate_upgrade_cost(self, new_plan):
        """Calcula el costo de upgrade a un nuevo plan (para implementación futura)"""
        if not hasattr(self, 'subscription'):
            return None
        
        current_plan = self.subscription.plan
        
        if new_plan.price <= current_plan.price:
            return {
                'is_upgrade': False,
                'cost': 0,
                'reason': 'El nuevo plan no es superior al actual'
            }
        
        # Cálculo básico para MVP (sin prorrateo)
        cost_difference = new_plan.price - current_plan.price
        
        return {
            'is_upgrade': True,
            'cost': cost_difference,
            'currency': new_plan.currency,
            'billing_cycle': new_plan.billing_cycle,
            'effective_date': 'immediate',  # Para MVP
            'proration': 0  # No implementado en MVP
        }
    
    # Método actualizado para compatibilidad con el sistema anterior
    def can_add_user(self):
        """Método de compatibilidad que considera suscripciones"""
        # Primero verificar límites de suscripción
        subscription_check = self.can_create_user_with_subscription()
        if subscription_check['subscription_required']:
            return False
        
        if not subscription_check['can_create']:
            return False
        
        # Si la suscripción permite, verificar límites legacy
        return super().can_add_user() if hasattr(super(), 'can_add_user') else True
    
    def can_add_user_detailed(self):
        """Método detallado que considera suscripciones"""
        # Verificar suscripción primero
        subscription_check = self.can_create_user_with_subscription()
        
        if subscription_check['subscription_required']:
            return {
                'can_add': False,
                'reason': subscription_check['reason'],
                'subscription_issue': True,
                'current_users': self.get_user_count(),
                'max_users': 0,
                'available_slots': 0
            }
        
        # Si la suscripción está bien, usar los límites del plan
        plan = self.get_current_plan()
        current_users = self.get_user_count()
        max_users = plan.max_users if plan else 0
        available_slots = max(0, max_users - current_users)
        
        return {
            'can_add': subscription_check['can_create'],
            'reason': subscription_check['reason'],
            'subscription_issue': False,
            'current_users': current_users,
            'max_users': max_users,
            'available_slots': available_slots,
            'active_users': self.get_active_user_count(),
            'inactive_users': self.get_inactive_user_count(),
            'total_users': current_users,
            'has_inactive_users': self.get_inactive_user_count() > 0,
            'is_at_limit': current_users >= max_users
        }    