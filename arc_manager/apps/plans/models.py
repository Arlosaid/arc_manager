# apps/plans/models.py
from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone

class Plan(models.Model):
    """Modelo mejorado para definir planes de la aplicación"""
    
    # Tipos de plan predefinidos para el MVP
    PLAN_TYPES = [
        ('trial', 'Prueba Gratuita'),
        ('basic', 'Plan Básico'),
        ('premium', 'Plan Premium'),  # Para escalabilidad futura
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Mensual'),
        ('annual', 'Anual'),
        ('trial', 'Prueba Gratuita'),
    ]
    
    # Información básica
    name = models.CharField("Nombre del plan", max_length=50, choices=PLAN_TYPES, unique=True)
    display_name = models.CharField("Nombre para mostrar", max_length=100)
    description = models.TextField("Descripción", blank=True)
    
    # Configuración de precios
    price = models.DecimalField("Precio", max_digits=10, decimal_places=2, default=0)
    currency = models.CharField("Moneda", max_length=3, default='MXN')
    billing_cycle = models.CharField("Ciclo de facturación", max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Límites del plan
    max_users = models.PositiveIntegerField("Máximo de usuarios", default=1)
    max_projects = models.PositiveIntegerField("Máximo de proyectos", default=1)
    storage_limit_gb = models.PositiveIntegerField("Límite de almacenamiento (GB)", default=1)
    
    # Características adicionales
    trial_days = models.PositiveIntegerField("Días de prueba", default=0, 
                                           help_text="Solo aplica para planes de prueba")
    features = models.JSONField("Características", default=dict, blank=True,
                               help_text="JSON con características específicas del plan")
    
    # Estado y configuración
    is_active = models.BooleanField("Activo", default=True)
    is_featured = models.BooleanField("Plan destacado", default=False)
    sort_order = models.PositiveIntegerField("Orden de visualización", default=0)
    
    # Para integración futura con Stripe
    stripe_price_id = models.CharField("Stripe Price ID", max_length=100, blank=True, null=True)
    stripe_product_id = models.CharField("Stripe Product ID", max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ['sort_order', 'price']
    
    def __str__(self):
        return self.display_name
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que los planes de prueba tengan días de prueba
        if self.name == 'trial' and self.trial_days == 0:
            raise ValidationError({
                'trial_days': 'Los planes de prueba deben tener días de prueba configurados.'
            })
        
        # Validar que solo un plan sea destacado por tipo de facturación
        if self.is_featured:
            featured_plans = Plan.objects.filter(
                is_featured=True, 
                billing_cycle=self.billing_cycle,
                is_active=True
            ).exclude(pk=self.pk)
            
            if featured_plans.exists():
                raise ValidationError({
                    'is_featured': f'Ya existe un plan destacado para el ciclo {self.get_billing_cycle_display()}.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_trial(self):
        """Retorna True si es un plan de prueba"""
        return self.name == 'trial'
    
    @property
    def price_display(self):
        """Retorna el precio formateado"""
        if self.price == 0:
            return "Gratis"
        return f"${self.price:,.0f} {self.currency}"
    
    @property
    def billing_display(self):
        """Retorna el ciclo de facturación formateado"""
        if self.is_trial:
            return f"{self.trial_days} días gratis"
        
        cycle_map = {
            'monthly': 'al mes',
            'annual': 'al año',
        }
        return cycle_map.get(self.billing_cycle, self.billing_cycle)
    
    def get_feature_list(self):
        """Retorna las características del plan como lista"""
        base_features = [
            f"Hasta {self.max_users} usuario{'s' if self.max_users != 1 else ''}",
            f"Hasta {self.max_projects} proyecto{'s' if self.max_projects != 1 else ''}",
            f"{self.storage_limit_gb} GB de almacenamiento"
        ]
        
        # Agregar características adicionales desde el campo JSON
        if self.features:
            additional_features = self.features.get('features', [])
            base_features.extend(additional_features)
        
        return base_features
    
    def can_create_users(self, current_count):
        """Verifica si se pueden crear más usuarios"""
        return current_count < self.max_users
    
    def can_create_projects(self, current_count):
        """Verifica si se pueden crear más proyectos"""
        return current_count < self.max_projects
    
    def get_usage_percentage(self, current_count, limit_type='users'):
        """Calcula el porcentaje de uso para un límite específico"""
        limits = {
            'users': self.max_users,
            'projects': self.max_projects,
            'storage': self.storage_limit_gb
        }
        
        max_limit = limits.get(limit_type, 1)
        if max_limit == 0:
            return 100
        
        return min((current_count / max_limit) * 100, 100)
    
    @classmethod
    def get_trial_plan(cls):
        """Retorna el plan de prueba activo"""
        try:
            return cls.objects.get(name='trial', is_active=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_basic_plan(cls):
        """Retorna el plan básico activo"""
        try:
            return cls.objects.get(name='basic', is_active=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_featured_plan(cls, billing_cycle='monthly'):
        """Retorna el plan destacado para un ciclo específico"""
        try:
            return cls.objects.get(
                is_featured=True, 
                billing_cycle=billing_cycle,
                is_active=True
            )
        except cls.DoesNotExist:
            return None

    @property
    def total_monthly_revenue(self):
        """Calcula los ingresos mensuales totales de este plan"""
        from apps.orgs.models import Organization  # Import local para evitar circular
        org_count = Organization.objects.filter(subscription__plan=self).count()
        return int(self.price * org_count)
    
    @property
    def usage_percentage(self):
        """Calcula el porcentaje de organizaciones que usan este plan"""
        from apps.orgs.models import Organization  # Import local para evitar circular
        total_orgs = Organization.objects.count()
        if total_orgs == 0:
            return 0
        org_count = Organization.objects.filter(subscription__plan=self).count()
        return int((org_count / total_orgs) * 100)

class Subscription(models.Model):
    """Modelo para gestionar suscripciones de organizaciones"""
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('trial', 'En Prueba'),
        ('expired', 'Expirada'),
        ('cancelled', 'Cancelada'),
        ('suspended', 'Suspendida'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Falló'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Relaciones
    organization = models.OneToOneField(
        'orgs.Organization',
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name="Organización"
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        verbose_name="Plan"
    )
    
    # Fechas importantes
    start_date = models.DateTimeField("Fecha de inicio", default=timezone.now)
    end_date = models.DateTimeField("Fecha de vencimiento")
    trial_end_date = models.DateTimeField("Fin de periodo de prueba", null=True, blank=True)
    
    # Estado de la suscripción
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='trial')
    payment_status = models.CharField("Estado de pago", max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Para facturación manual en MVP
    last_payment_date = models.DateTimeField("Último pago", null=True, blank=True)
    next_billing_date = models.DateTimeField("Próxima facturación", null=True, blank=True)
    
    # Para integración futura con Stripe
    stripe_subscription_id = models.CharField("Stripe Subscription ID", max_length=100, blank=True, null=True)
    stripe_customer_id = models.CharField("Stripe Customer ID", max_length=100, blank=True, null=True)
    
    # Configuración
    auto_renew = models.BooleanField("Renovación automática", default=True)
    cancel_at_period_end = models.BooleanField("Cancelar al final del periodo", default=False)
    
    # Metadatos
    metadata = models.JSONField("Metadatos", default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.plan.display_name}"
    
    def save(self, *args, **kwargs):
        # Configurar fechas automáticamente para nuevas suscripciones
        if not self.pk:
            self.setup_subscription_dates()
        super().save(*args, **kwargs)
    
    def setup_subscription_dates(self):
        """Configura las fechas de la suscripción basado en el plan"""
        now = timezone.now()
        
        if self.plan.is_trial:
            # Para planes de prueba
            self.status = 'trial'
            self.trial_end_date = now + timedelta(days=self.plan.trial_days)
            self.end_date = self.trial_end_date
        else:
            # Para planes de pago
            if self.plan.billing_cycle == 'monthly':
                self.end_date = now + timedelta(days=30)
                self.next_billing_date = self.end_date
            elif self.plan.billing_cycle == 'annual':
                self.end_date = now + timedelta(days=365)
                self.next_billing_date = self.end_date
    
    @property
    def is_active(self):
        """Verifica si la suscripción está activa"""
        now = timezone.now()
        return self.status in ['active', 'trial'] and self.end_date > now
    
    @property
    def is_trial(self):
        """Verifica si está en periodo de prueba"""
        return self.status == 'trial'
    
    @property
    def is_expired(self):
        """Verifica si la suscripción ha expirado"""
        return self.end_date <= timezone.now()
    
    @property
    def days_remaining(self):
        """Calcula los días restantes de la suscripción"""
        if self.is_expired:
            return 0
        
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
    
    @property
    def trial_days_remaining(self):
        """Calcula los días restantes del periodo de prueba"""
        if not self.is_trial or not self.trial_end_date:
            return 0
        
        if self.trial_end_date <= timezone.now():
            return 0
        
        delta = self.trial_end_date - timezone.now()
        return max(0, delta.days)
    
    def extend_subscription(self, days=None):
        """Extiende la suscripción por un número de días"""
        if days is None:
            # Extensión estándar basada en el ciclo de facturación
            if self.plan.billing_cycle == 'monthly':
                days = 30
            elif self.plan.billing_cycle == 'annual':
                days = 365
            else:
                days = 30  # Por defecto
        
        self.end_date += timedelta(days=days)
        if self.next_billing_date:
            self.next_billing_date += timedelta(days=days)
        self.save()
    
    def cancel_subscription(self, immediate=False):
        """Cancela la suscripción"""
        if immediate:
            self.status = 'cancelled'
            self.end_date = timezone.now()
        else:
            self.cancel_at_period_end = True
        
        self.auto_renew = False
        self.save()
    
    def reactivate_subscription(self):
        """Reactiva una suscripción cancelada o expirada"""
        if self.status in ['cancelled', 'expired']:
            self.status = 'active'
            self.cancel_at_period_end = False
            self.auto_renew = True
            
            # Extender la suscripción si ha expirado
            if self.is_expired:
                self.extend_subscription()
            
            self.save()
    
    def upgrade_plan(self, new_plan):
        """Cambia a un plan superior"""
        old_plan = self.plan
        self.plan = new_plan
        
        # Calcular prorrateo si es necesario (para implementación futura)
        # Por ahora, simplemente cambiar el plan
        
        self.save()
        
        return {
            'old_plan': old_plan,
            'new_plan': new_plan,
            'effective_date': timezone.now()
        }
    
    def check_and_update_status(self):
        """Verifica y actualiza el estado de la suscripción"""
        now = timezone.now()
        
        if self.is_trial and self.trial_end_date and now >= self.trial_end_date:
            # El periodo de prueba ha terminado
            if self.cancel_at_period_end:
                self.status = 'cancelled'
            else:
                # Cambiar a plan básico o expirar
                basic_plan = Plan.get_basic_plan()
                if basic_plan and self.payment_status == 'paid':
                    self.status = 'active'
                    self.plan = basic_plan
                else:
                    self.status = 'expired'
        
        elif now >= self.end_date:
            # La suscripción ha expirado
            if self.cancel_at_period_end or not self.auto_renew:
                self.status = 'cancelled'
            else:
                self.status = 'expired'
        
        self.save()
        return self.status        

class UpgradeRequest(models.Model):
    """Modelo para gestionar solicitudes de upgrade de manera controlada"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente de Aprobación'),
        ('approved', 'Aprobada - Pendiente de Pago'),
        ('payment_pending', 'Pago Reportado - En Verificación'), 
        ('completed', 'Completada'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Cancelada'),
    ]
    
    # Información básica
    organization = models.ForeignKey(
        'orgs.Organization',
        on_delete=models.CASCADE,
        related_name='upgrade_requests',
        verbose_name="Organización"
    )
    current_plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='current_upgrades',
        verbose_name="Plan Actual"
    )
    requested_plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='requested_upgrades',
        verbose_name="Plan Solicitado"
    )
    
    # Estado y fechas
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_date = models.DateTimeField("Fecha de Solicitud", auto_now_add=True)
    approved_date = models.DateTimeField("Fecha de Aprobación", null=True, blank=True)
    completed_date = models.DateTimeField("Fecha de Completado", null=True, blank=True)
    
    # Usuarios involucrados
    requested_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='upgrade_requests_made',
        verbose_name="Solicitado por"
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='upgrade_requests_approved',
        verbose_name="Aprobado por"
    )
    
    # Información de pago
    amount_due = models.DecimalField("Monto a Pagar", max_digits=10, decimal_places=2)
    payment_method = models.CharField("Método de Pago Preferido", max_length=50, blank=True)
    payment_reference = models.CharField("Referencia de Pago", max_length=100, blank=True)
    payment_proof_info = models.CharField("Información del Comprobante", max_length=200, blank=True, 
                                        help_text="Descripción del comprobante de pago enviado por email o WhatsApp")
    
    # Notas y comentarios
    request_notes = models.TextField("Notas de la Solicitud", blank=True)
    admin_notes = models.TextField("Notas del Administrador", blank=True)
    rejection_reason = models.TextField("Motivo de Rechazo", blank=True)
    
    # Información de contacto para pago
    contact_info = models.JSONField("Información de Contacto", default=dict, blank=True)
    
    class Meta:
        verbose_name = "Solicitud de Upgrade"
        verbose_name_plural = "Solicitudes de Upgrade"
        ordering = ['-requested_date']
    
    def __str__(self):
        return f"{self.organization.name} - {self.current_plan.display_name} → {self.requested_plan.display_name}"
    
    @property
    def price_difference(self):
        """Diferencia de precio entre planes"""
        return self.requested_plan.price - self.current_plan.price
    
    def approve(self, approved_by_user, admin_notes=""):
        """Aprobar la solicitud de upgrade"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_date = timezone.now()
        self.admin_notes = admin_notes
        self.save()
        
        # Enviar email con información de pago
        self._send_payment_instructions()
    
    def reject(self, rejected_by_user, reason=""):
        """Rechazar la solicitud de upgrade"""
        self.status = 'rejected'
        self.approved_by = rejected_by_user
        self.approved_date = timezone.now()
        self.rejection_reason = reason
        self.save()
        
        # Enviar email de rechazo
        self._send_rejection_email()
    
    def mark_payment_received(self, payment_reference="", payment_proof=None):
        """Marcar que se recibió el pago"""
        self.status = 'payment_pending'
        self.payment_reference = payment_reference
        if payment_proof:
            self.payment_proof_info = payment_proof
        self.save()
        
        # Notificar al admin para verificar pago
        self._notify_payment_received()
    
    def complete_upgrade(self, completed_by_user):
        """Completar el upgrade aplicando el nuevo plan"""
        if self.status != 'payment_pending':
            raise ValueError("Solo se pueden completar upgrades con pago pendiente")
        
        # Actualizar la suscripción
        subscription = self.organization.subscription
        old_plan = subscription.plan
        
        subscription.plan = self.requested_plan
        subscription.payment_status = 'paid'
        subscription.last_payment_date = timezone.now()
        
        # Extender la suscripción
        subscription.extend_subscription()
        
        # Agregar al historial de pagos
        if not subscription.metadata:
            subscription.metadata = {}
        
        payment_history = subscription.metadata.get('payment_history', [])
        payment_history.append({
            'date': timezone.now().isoformat(),
            'amount': float(self.amount_due),
            'method': self.payment_method or 'transferencia',
            'reference': self.payment_reference,
            'status': 'paid',
            'upgrade_request_id': self.id,
            'old_plan': old_plan.display_name,
            'new_plan': self.requested_plan.display_name,
            'processed_by': completed_by_user.username
        })
        subscription.metadata['payment_history'] = payment_history
        subscription.save()
        
        # Marcar como completado
        self.status = 'completed'
        self.completed_date = timezone.now()
        self.save()
        
        # Enviar confirmación
        self._send_completion_email()
        
        return subscription
    
    def cancel(self, cancelled_by_user, reason=""):
        """Cancelar la solicitud"""
        self.status = 'cancelled'
        self.approved_by = cancelled_by_user
        self.admin_notes = f"Cancelada: {reason}"
        self.save()
    
    def _send_payment_instructions(self):
        """Enviar instrucciones de pago al usuario"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Información bancaria para el pago
        bank_info = getattr(settings, 'PAYMENT_BANK_INFO', {
            'bank_name': 'Banco Ejemplo',
            'account_holder': 'Tu Empresa SA de CV',
            'account_number': 'XXXX-XXXX-XXXX-1234',
            'clabe': '012345678901234567',
            'concept': f'Upgrade Plan - {self.organization.slug}'
        })
        
        subject = f'✅ Solicitud de Upgrade Aprobada - {self.requested_plan.display_name}'
        message = f"""
¡Hola!

Tu solicitud de upgrade ha sido APROBADA 🎉

DETALLES DEL UPGRADE:
━━━━━━━━━━━━━━━━━━━━━━━━
• Organización: {self.organization.name}
• Plan actual: {self.current_plan.display_name} (${self.current_plan.price}/mes)
• Plan nuevo: {self.requested_plan.display_name} (${self.requested_plan.price}/mes)
• Monto a pagar: ${self.amount_due}/mes

INFORMACIÓN PARA EL PAGO:
━━━━━━━━━━━━━━━━━━━━━━━━
• Banco: {bank_info.get('bank_name')}
• Beneficiario: {bank_info.get('account_holder')}
• Cuenta: {bank_info.get('account_number')}
• CLABE: {bank_info.get('clabe')}
• Concepto: {bank_info.get('concept')}
• Monto: ${self.amount_due} MXN

PRÓXIMOS PASOS:
━━━━━━━━━━━━━━━━━━━━━━━━
1. Realiza la transferencia bancaria
2. Guarda tu comprobante de pago
3. Reporta tu pago en tu dashboard
4. Nosotros verificaremos y activaremos tu nuevo plan

⚠️ IMPORTANTE: Una vez que reportes tu pago, verificaremos la información y activaremos tu nuevo plan en máximo 24 horas.

¿Tienes dudas? Contáctanos:
📧 soporte@tudominio.com
📱 +52 55 1234 5678

¡Gracias por confiar en nosotros!
        """
        
        # Enviar a todos los admins de la organización
        admin_emails = []
        for user in self.organization.users.filter(is_org_admin=True, is_active=True):
            admin_emails.append(user.email)
        
        if admin_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
                recipient_list=admin_emails,
                fail_silently=True
            )
    
    def _send_rejection_email(self):
        """Enviar email de rechazo"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'❌ Solicitud de Upgrade Rechazada'
        message = f"""
Hola,

Lamentamos informarte que tu solicitud de upgrade ha sido rechazada.

DETALLES:
• Organización: {self.organization.name}
• Plan solicitado: {self.requested_plan.display_name}
• Motivo: {self.rejection_reason or 'No se proporcionó motivo específico'}

Si tienes dudas sobre esta decisión, puedes contactarnos:
📧 soporte@tudominio.com
📱 +52 55 1234 5678

Puedes realizar una nueva solicitud cuando hayas resuelto los puntos mencionados.
        """
        
        admin_emails = [user.email for user in self.organization.users.filter(is_org_admin=True, is_active=True)]
        
        if admin_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
                recipient_list=admin_emails,
                fail_silently=True
            )
    
    def _send_completion_email(self):
        """Enviar email de upgrade completado"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'🎉 ¡Upgrade Completado! - {self.requested_plan.display_name}'
        message = f"""
¡Felicidades! 🎉

Tu upgrade ha sido completado exitosamente.

DETALLES:
• Organización: {self.organization.name}
• Plan anterior: {self.current_plan.display_name}
• Plan actual: {self.requested_plan.display_name}
• Fecha de activación: {self.completed_date.strftime('%d/%m/%Y %H:%M')}

Ya puedes acceder a todas las funcionalidades de tu nuevo plan.

¡Gracias por confiar en nosotros!
        """
        
        admin_emails = [user.email for user in self.organization.users.filter(is_org_admin=True, is_active=True)]
        
        if admin_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
                recipient_list=admin_emails,
                fail_silently=True
            )
    
    def _notify_payment_received(self):
        """Notificar al admin que se recibió un reporte de pago"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'💰 Pago Reportado - Verificar: {self.organization.name}'
        message = f"""
Se ha reportado un pago para verificación:

DETALLES DEL UPGRADE:
• Organización: {self.organization.name}
• Plan: {self.current_plan.display_name} → {self.requested_plan.display_name}
• Monto: ${self.amount_due}
• Referencia reportada: {self.payment_reference}

Por favor verifica el pago y completa el upgrade en el panel de administración.

URL: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/plans/upgraderequest/{self.id}/change/
        """
        
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@tudominio.com')
        
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
            recipient_list=[admin_email],
            fail_silently=True
        )        