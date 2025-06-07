# apps/plans/services.py
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import Plan, Subscription

class SubscriptionService:
    """Servicio para gestionar suscripciones"""
    
    @staticmethod
    def create_trial_subscription(organization):
        """Crea una suscripción de prueba para una organización"""
        trial_plan = Plan.get_trial_plan()
        
        if not trial_plan:
            raise ValueError("No hay plan de prueba disponible")
        
        # Verificar si ya tiene una suscripción
        if hasattr(organization, 'subscription'):
            raise ValueError("La organización ya tiene una suscripción")
        
        subscription = Subscription.objects.create(
            organization=organization,
            plan=trial_plan,
            status='trial'
        )
        
        return subscription
    
    @staticmethod
    def upgrade_to_basic(organization, payment_method='manual'):
        """Actualiza una organización al plan básico"""
        basic_plan = Plan.get_basic_plan()
        
        if not basic_plan:
            raise ValueError("Plan básico no disponible")
        
        subscription = organization.subscription
        
        if subscription.plan.name == 'basic':
            raise ValueError("Ya está en el plan básico")
        
        # Actualizar suscripción
        old_plan = subscription.plan
        subscription.plan = basic_plan
        subscription.status = 'active'
        subscription.payment_status = 'paid' if payment_method == 'paid' else 'pending'
        
        # Configurar nuevas fechas
        now = timezone.now()
        if basic_plan.billing_cycle == 'monthly':
            subscription.end_date = now + timedelta(days=30)
            subscription.next_billing_date = subscription.end_date
        
        subscription.save()
        
        return {
            'subscription': subscription,
            'old_plan': old_plan,
            'new_plan': basic_plan
        }
    
    @staticmethod
    def process_manual_payment(organization, amount, payment_reference=None):
        """Procesa un pago manual para la suscripción"""
        subscription = organization.subscription
        
        if not subscription:
            raise ValueError("No hay suscripción para procesar")
        
        # Verificar el monto
        if amount != subscription.plan.price:
            raise ValueError(f"Monto incorrecto. Se esperaba {subscription.plan.price}")
        
        # Procesar pago
        subscription.payment_status = 'paid'
        subscription.last_payment_date = timezone.now()
        
        # Extender suscripción
        if subscription.status == 'expired' or subscription.is_expired:
            subscription.reactivate_subscription()
        else:
            subscription.extend_subscription()
        
        # Guardar referencia de pago en metadatos
        if payment_reference:
            if not subscription.metadata:
                subscription.metadata = {}
            subscription.metadata['last_payment_reference'] = payment_reference
            subscription.metadata['payment_history'] = subscription.metadata.get('payment_history', [])
            subscription.metadata['payment_history'].append({
                'amount': float(amount),
                'reference': payment_reference,
                'date': timezone.now().isoformat(),
                'method': 'manual'
            })
        
        subscription.save()
        
        return subscription
    
    @staticmethod
    def check_subscription_limits(organization, limit_type, current_count):
        """Verifica si la organización puede crear más recursos"""
        subscription = organization.subscription
        
        if not subscription or not subscription.is_active:
            return {
                'can_create': False,
                'reason': 'Suscripción inactiva o expirada',
                'current': current_count,
                'limit': 0
            }
        
        plan = subscription.plan
        
        limits = {
            'users': plan.max_users,
            'projects': plan.max_projects,
            'storage_gb': plan.storage_limit_gb
        }
        
        limit = limits.get(limit_type, 0)
        can_create = current_count < limit
        
        return {
            'can_create': can_create,
            'reason': 'Límite alcanzado' if not can_create else 'OK',
            'current': current_count,
            'limit': limit,
            'usage_percentage': plan.get_usage_percentage(current_count, limit_type)
        }
    
    @staticmethod
    def get_organizations_expiring_soon(days=7):
        """Obtiene organizaciones con suscripciones que expiran pronto"""
        cutoff_date = timezone.now() + timedelta(days=days)
        
        return Subscription.objects.filter(
            status__in=['active', 'trial'],
            end_date__lte=cutoff_date,
            end_date__gt=timezone.now()
        ).select_related('organization', 'plan')
    
    @staticmethod
    def send_expiration_notifications():
        """Envía notificaciones de expiración próxima"""
        # Notificaciones a 7 días
        subscriptions_7_days = SubscriptionService.get_organizations_expiring_soon(7)
        
        for subscription in subscriptions_7_days:
            SubscriptionService._send_expiration_email(
                subscription, 
                days_remaining=subscription.days_remaining
            )
        
        # Notificaciones a 3 días
        subscriptions_3_days = SubscriptionService.get_organizations_expiring_soon(3)
        
        for subscription in subscriptions_3_days:
            SubscriptionService._send_expiration_email(
                subscription, 
                days_remaining=subscription.days_remaining,
                urgent=True
            )
        
        return {
            'sent_7_days': len(subscriptions_7_days),
            'sent_3_days': len(subscriptions_3_days)
        }
    
    @staticmethod
    def _send_expiration_email(subscription, days_remaining, urgent=False):
        """Envía email de notificación de expiración"""
        organization = subscription.organization
        plan = subscription.plan
        
        # Obtener email del admin de la organización
        admin_users = organization.users.filter(is_org_admin=True, is_active=True)
        if not admin_users.exists():
            return False
        
        subject_prefix = "🚨 URGENTE" if urgent else "📅 Recordatorio"
        
        subject = f"{subject_prefix}: Tu suscripción a {plan.display_name} expira en {days_remaining} días"
        
        message = f"""
Hola,

Tu suscripción al {plan.display_name} para la organización "{organization.name}" expirará en {days_remaining} días.

Detalles de la suscripción:
- Plan: {plan.display_name}
- Precio: {plan.price_display}
- Fecha de expiración: {subscription.end_date.strftime('%d/%m/%Y')}

Para renovar tu suscripción, contacta a nuestro equipo de ventas o accede a tu panel de control.

¡Gracias por usar nuestro servicio!

El equipo de {getattr(settings, 'SITE_NAME', 'ARC Manager')}
"""
        
        try:
            for admin in admin_users:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
                    recipient_list=[admin.email],
                    fail_silently=False
                )
            return True
        except Exception as e:
            print(f"Error enviando email de expiración: {e}")
            return False
    
    @staticmethod
    def expire_subscriptions():
        """Expira suscripciones que han vencido"""
        now = timezone.now()
        
        expired_subscriptions = Subscription.objects.filter(
            status__in=['active', 'trial'],
            end_date__lte=now
        )
        
        count = 0
        for subscription in expired_subscriptions:
            subscription.check_and_update_status()
            count += 1
        
        return count
    
    @staticmethod
    def get_subscription_stats():
        """Obtiene estadísticas de suscripciones"""
        total_subscriptions = Subscription.objects.count()
        active_subscriptions = Subscription.objects.filter(status='active').count()
        trial_subscriptions = Subscription.objects.filter(status='trial').count()
        expired_subscriptions = Subscription.objects.filter(status='expired').count()
        
        # Ingresos mensuales estimados
        monthly_revenue = Subscription.objects.filter(
            status='active',
            plan__billing_cycle='monthly'
        ).aggregate(
            total=models.Sum('plan__price')
        )['total'] or 0
        
        return {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'trial_subscriptions': trial_subscriptions,
            'expired_subscriptions': expired_subscriptions,
            'monthly_revenue': monthly_revenue,
            'conversion_rate': (active_subscriptions / max(total_subscriptions, 1)) * 100
        }