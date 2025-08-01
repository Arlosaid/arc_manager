# apps/plans/services.py - Sistema de Suscripciones MVP Optimizado
from django.utils import timezone
from django.db import transaction
import logging

from .models import Plan, Subscription, Payment

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Servicio simplificado para gestionar la creación de suscripciones.
    El resto de la lógica de negocio se maneja en los modelos y el admin.
    """
    
    @staticmethod
    def create_trial_subscription(organization):
        """
        Crea una suscripción trial automática para nuevas organizaciones.
        """
        logger.info(f"Creando suscripción trial para {organization.name}")
        
        try:
            if hasattr(organization, 'subscription'):
                logger.warning(f"La organización {organization.name} ya tiene una suscripción.")
                return {'success': False, 'error': 'La organización ya tiene una suscripción.'}
            
            trial_plan = Plan.get_trial_plan()
            if not trial_plan:
                logger.error("No se encontró un plan de prueba (trial) activo.")
                return {'success': False, 'error': 'No hay plan trial configurado en el sistema.'}
            
            with transaction.atomic():
                subscription = Subscription.objects.create(
                    organization=organization,
                    plan=trial_plan
                )
                
                Payment.objects.create(
                    subscription=subscription,
                    amount=0,
                    payment_method='system',
                    payment_type='trial_to_paid',
                    status='completed',
                    processed_by='system',
                    description=f'Activación de trial automática - {trial_plan.display_name}',
                    days_added=trial_plan.trial_days or 30
                )
            
            logger.info(f"Suscripción trial creada exitosamente para {organization.name}")
            return {'success': True, 'subscription': subscription}
            
        except Exception as e:
            logger.error(f"Error creando suscripción trial para {organization.name}: {str(e)}", exc_info=True)
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    @staticmethod
    def get_subscription_or_create(organization):
        """
        Obtiene la suscripción de una organización o crea una trial si no existe.
        Es un método de conveniencia para asegurar que una organización siempre tenga suscripción.
        """
        try:
            subscription = getattr(organization, 'subscription', None)
            if not subscription:
                result = SubscriptionService.create_trial_subscription(organization)
                return result.get('subscription') if result['success'] else None
            return subscription
            
        except Exception as e:
            logger.error(f"Error obteniendo o creando suscripción para {organization.name}: {str(e)}", exc_info=True)
            return None