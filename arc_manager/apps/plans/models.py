# apps/plans/models.py
from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
import logging

class Plan(models.Model):
    """
    Modelo simplificado para definir los planes de la aplicación para el MVP.
    """
    PLAN_TYPES = [
        ('trial', 'Prueba Gratuita'),
        ('basic', 'Plan Básico'),
    ]
    
    # Información básica
    name = models.CharField("Nombre del plan", max_length=50, choices=PLAN_TYPES, unique=True)
    display_name = models.CharField("Nombre para mostrar", max_length=100)
    description = models.TextField("Descripción", blank=True)
    
    # Configuración de precios
    price = models.DecimalField("Precio", max_digits=10, decimal_places=2, default=0)
    
    # Límites del plan para el MVP
    max_users = models.PositiveIntegerField("Máximo de usuarios", default=1)
    
    # Características adicionales
    trial_days = models.PositiveIntegerField("Días de prueba", default=0, help_text="Para planes 'trial', establece la duración de la prueba.")
    billing_cycle_days = models.PositiveIntegerField("Días del ciclo de facturación", default=30, help_text="Duración estándar del ciclo de pago en días.")
    grace_period_days = models.PositiveIntegerField("Días de gracia", default=0, help_text="Días de gracia después de la expiración antes de restringir el acceso.")
    
    # Estado y configuración
    is_active = models.BooleanField("Activo", default=True)
    
    # Timestamps
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ['price']
    
    def __str__(self):
        return self.display_name
    
    def get_feature_list(self):
        """Retorna las características del plan como una lista simple."""
        return [f"Hasta {self.max_users} usuario{'s' if self.max_users != 1 else ''}"]

    @property
    def is_trial(self):
        return self.name == 'trial'

    # Métodos de clase para obtener planes comunes
    @classmethod
    def get_trial_plan(cls):
        try:
            return cls.objects.get(name='trial', is_active=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_basic_plan(cls):
        try:
            return cls.objects.get(name='basic', is_active=True)
        except cls.DoesNotExist:
            return None

    def get_usage_percentage(self, current_value, limit_type):
        """Calcula el porcentaje de uso para un límite específico de forma simple."""
        limit = 0
        if limit_type == 'users':
            limit = self.max_users
        
        if not limit or limit == 0:
            return 100 if current_value > 0 else 0
        
        percentage = (current_value / limit) * 100
        return min(100, round(percentage))


class Subscription(models.Model):
    """
    Modelo simplificado para gestionar las suscripciones de las organizaciones.
    """
    SUBSCRIPTION_STATUS_CHOICES = [
        ('trial_active', 'Trial Activo'),
        ('trial_expired', 'Trial Expirado'),
        ('basic_active', 'Plan Básico Activo'),
        ('basic_grace', 'Plan Básico en Gracia'),
        ('basic_expired', 'Plan Básico Expirado'),
    ]
    
    organization = models.OneToOneField('orgs.Organization', on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, verbose_name="Plan Actual")
    
    start_date = models.DateTimeField("Fecha de inicio", default=timezone.now)
    end_date = models.DateTimeField("Fecha de vencimiento", null=True, blank=True)
    grace_end_date = models.DateTimeField("Fin del período de gracia", null=True, blank=True)
    
    subscription_status = models.CharField("Estado de Suscripción", max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='trial_active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name} - {self.plan.display_name}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            self.setup_initial_subscription(self.plan)
            self.save(update_fields=['start_date', 'end_date', 'subscription_status'])

    def setup_initial_subscription(self, plan):
        """Configura las fechas y el estado inicial de la suscripción."""
        now = timezone.now()
        self.start_date = now
        days = plan.trial_days if plan.is_trial else plan.billing_cycle_days
        self.end_date = now + timedelta(days=days)
        self.subscription_status = f'{plan.name}_active'

    def calculate_current_status(self):
        """Calcula el estado de la suscripción basado en las fechas, sin modificar el estado."""
        now = timezone.now()
        plan_prefix = self.plan.name
        
        # Si la fecha de vencimiento no ha pasado, está activo
        if self.end_date and now <= self.end_date:
            return f'{plan_prefix}_active'
        
        # Si tiene período de gracia, verificar si estamos dentro de él
        if self.plan.grace_period_days > 0:
            # La fecha de fin de gracia se calcula dinámicamente
            grace_end_date = self.end_date + timedelta(days=self.plan.grace_period_days)
            if now <= grace_end_date:
                return f'{plan_prefix}_grace'

        # Si ninguna de las condiciones anteriores se cumple, ha expirado
        return f'{plan_prefix}_expired'

    def update_status(self):
        """Actualiza el estado si ha cambiado. Usado en vistas y cron jobs."""
        new_status = self.calculate_current_status()
        if new_status != self.subscription_status:
            self.subscription_status = new_status
            
            # Si la suscripción entra en período de gracia, calcula y guarda la fecha de fin de gracia
            if new_status.endswith('_grace') and not self.grace_end_date:
                self.grace_end_date = self.end_date + timedelta(days=self.plan.grace_period_days)

            self.save(update_fields=['subscription_status', 'grace_end_date', 'updated_at'])
            return True
        return False

    @property
    def is_active(self):
        return self.subscription_status.endswith('_active')

    @property
    def is_in_grace_period(self):
        return self.subscription_status.endswith('_grace')
    
    @property
    def is_expired(self):
        return self.subscription_status.endswith('_expired')

    @property
    def days_remaining(self):
        """Calcula los días restantes de forma precisa según el estado de la suscripción."""
        now = timezone.now()

        if self.is_active and self.end_date:
            remaining = self.end_date - now
        elif self.is_in_grace_period and self.grace_end_date:
            remaining = self.grace_end_date - now
        else:
            return 0  # Expirado o sin fecha de referencia

        return max(0, remaining.days)

    def process_payment(self, amount, processed_by):
        """Procesa un pago, extiende la suscripción y crea un registro de pago."""
        now = timezone.now()
        old_end_date = self.end_date
        
        # Extender desde la fecha de vencimiento si aún no ha pasado, o desde hoy si ya expiró.
        base_date = max(now, self.end_date or now)
        self.end_date = base_date + timedelta(days=self.plan.billing_cycle_days)
        
        self.subscription_status = f'{self.plan.name}_active'
        self.grace_end_date = None # Reiniciar el periodo de gracia
        
        payment = Payment.objects.create(
            subscription=self,
            amount=amount,
            payment_method='manual',
            payment_type='subscription',
            status='completed',
            processed_by=processed_by,
            description=f'Pago procesado para extender el plan {self.plan.display_name}',
            days_added=self.plan.billing_cycle_days,
            old_end_date=old_end_date,
            new_end_date=self.end_date
        )
        self.save()
        return {'success': True, 'payment_id': payment.id}

    def switch_plan(self, new_plan, processed_by):
        """Cambia el plan de la suscripción, reinicia las fechas y crea un registro."""
        now = timezone.now()
        old_plan_display = self.plan.display_name
        
        self.plan = new_plan
        self.start_date = now
        self.end_date = now + timedelta(days=new_plan.billing_cycle_days)
        self.subscription_status = f'{new_plan.name}_active'
        self.grace_end_date = None

        payment = Payment.objects.create(
            subscription=self,
            amount=new_plan.price,
            payment_method='upgrade',
            payment_type='upgrade',
            status='completed',
            processed_by=processed_by,
            description=f'Upgrade de plan: {old_plan_display} -> {new_plan.display_name}',
            days_added=new_plan.billing_cycle_days
        )
        self.save()
        return {'success': True, 'payment_id': payment.id}

    def get_payment_history(self, limit=10):
        return self.payments.filter(status='completed').order_by('-created_at')[:limit]


class Payment(models.Model):
    """Modelo para registrar todos los pagos y transacciones, simplificado para MVP."""
    PAYMENT_STATUS = [('completed', 'Completado')]
    PAYMENT_METHODS = [('manual', 'Pago Manual'), ('upgrade', 'Upgrade')]
    PAYMENT_TYPES = [('subscription', 'Suscripción'), ('upgrade', 'Upgrade'), ('trial_to_paid', 'Activación Trial')]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField("Monto", max_digits=10, decimal_places=2)
    payment_method = models.CharField("Método de Pago", max_length=20, choices=PAYMENT_METHODS, default='manual')
    payment_type = models.CharField("Tipo de Pago", max_length=20, choices=PAYMENT_TYPES, default='subscription')
    status = models.CharField("Estado", max_length=20, choices=PAYMENT_STATUS, default='completed')
    processed_by = models.CharField("Procesado por", max_length=100, blank=True, null=True)
    description = models.TextField("Descripción", blank=True)
    days_added = models.PositiveIntegerField("Días agregados", default=0)
    
    old_end_date = models.DateTimeField("Fecha anterior de vencimiento", null=True, blank=True)
    new_end_date = models.DateTimeField("Nueva fecha de vencimiento", null=True, blank=True)
    
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscription.organization.name} - ${self.amount} ({self.get_status_display()})"


class UpgradeRequest(models.Model):
    """Gestiona las solicitudes de los usuarios para cambiar a un plan superior."""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    
    organization = models.ForeignKey('orgs.Organization', on_delete=models.CASCADE, related_name='upgrade_requests')
    current_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='+')
    requested_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='+')
    
    amount = models.DecimalField("Monto del upgrade", max_digits=10, decimal_places=2)
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.CharField("Aprobado por", max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud de Upgrade"
        verbose_name_plural = "Solicitudes de Upgrade"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name}: {self.current_plan.display_name} -> {self.requested_plan.display_name}"

    def approve(self, approved_by_user):
        """Aprueba la solicitud, actualiza el estado y ejecuta el cambio de plan en la suscripción."""
        from django.db import transaction
        
        logger = logging.getLogger(__name__)
        
        if self.status != 'pending':
            return {'success': False, 'error': 'La solicitud no está pendiente.'}

        try:
            with transaction.atomic():
                self.status = 'approved'
                self.approved_by = approved_by_user.username
                self.save()
                
                subscription = self.organization.subscription
                result = subscription.switch_plan(
                    new_plan=self.requested_plan,
                    processed_by=self.approved_by
                )
                
                if result['success']:
                    logger.info(f"Upgrade a {self.requested_plan.display_name} completado para {self.organization.name}.")
                    return {'success': True}
                else:
                    # Si switch_plan falla, la transacción se revierte, así que no es necesario
                    # revertir manualmente el estado de la solicitud.
                    raise Exception("Fallo al cambiar el plan en la suscripción.")

        except Exception as e:
            logger.error(f"Error al aprobar la solicitud de upgrade {self.id}: {str(e)}", exc_info=True)
            return {'success': False, 'error': f'Error interno: {str(e)}'}        
