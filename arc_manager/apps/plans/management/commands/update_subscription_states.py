from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.plans.models import Subscription
from apps.plans.services import SubscriptionService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualiza automáticamente los estados de suscripción basado en fechas - Para uso en cron jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué cambios se harían sin ejecutarlos',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada de cada suscripción procesada',
        )
        parser.add_argument(
            '--filter-status',
            type=str,
            help='Filtrar por estado específico (ej: trial_active, basic_active)',
        )
        parser.add_argument(
            '--org-id',
            type=int,
            help='Procesar solo una organización específica por ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        filter_status = options['filter_status']
        org_id = options['org_id']
        
        self.stdout.write(self.style.SUCCESS('🔄 Iniciando actualización de estados de suscripción'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: No se realizarán cambios reales'))
        
        try:
            # Obtener suscripciones a procesar
            subscriptions = Subscription.objects.select_related('organization', 'plan')
            
            if org_id:
                subscriptions = subscriptions.filter(organization__id=org_id)
                self.stdout.write(f'📋 Procesando solo organización ID: {org_id}')
            
            if filter_status:
                subscriptions = subscriptions.filter(subscription_status=filter_status)
                self.stdout.write(f'📋 Procesando solo estado: {filter_status}')
            
            total_subscriptions = subscriptions.count()
            
            if total_subscriptions == 0:
                self.stdout.write(self.style.WARNING('❌ No hay suscripciones para procesar'))
                return
            
            self.stdout.write(f'📊 Total de suscripciones a procesar: {total_subscriptions}')
            
            # Contadores para estadísticas
            stats = {
                'processed': 0,
                'changed': 0,
                'errors': 0,
                'expired': 0,
                'grace_period': 0,
                'reactivated': 0,
                'status_changes': {}
            }
            
            # Procesar cada suscripción
            for subscription in subscriptions:
                try:
                    stats['processed'] += 1
                    
                    if verbose:
                        self.stdout.write(f'  📋 Procesando: {subscription.organization.name} ({subscription.subscription_status})')
                    
                    # Obtener estado actual y nuevo
                    old_status = subscription.subscription_status
                    new_status = subscription.calculate_current_status()
                    
                    if old_status != new_status:
                        stats['changed'] += 1
                        
                        # Registrar cambio de estado
                        change_key = f"{old_status} → {new_status}"
                        stats['status_changes'][change_key] = stats['status_changes'].get(change_key, 0) + 1
                        
                        # Clasificar el tipo de cambio
                        if new_status.endswith('_expired'):
                            stats['expired'] += 1
                        elif new_status.endswith('_grace'):
                            stats['grace_period'] += 1
                        elif new_status.endswith('_active') and old_status.endswith('_expired'):
                            stats['reactivated'] += 1
                        
                        if not dry_run:
                            # Usar el servicio para actualizar el estado
                            result = SubscriptionService.update_subscription_status(subscription)
                            
                            if result['success']:
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✅ {subscription.organization.name}: {old_status} → {new_status}')
                                )
                            else:
                                self.stdout.write(
                                    self.style.ERROR(f'  ❌ Error actualizando {subscription.organization.name}: {result["error"]}')
                                )
                                stats['errors'] += 1
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'  🔄 [DRY-RUN] {subscription.organization.name}: {old_status} → {new_status}')
                            )
                    else:
                        if verbose:
                            self.stdout.write(f'  ✅ {subscription.organization.name}: Sin cambios ({old_status})')
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Error procesando {subscription.organization.name}: {str(e)}')
                    )
                    logger.error(f'Error procesando suscripción {subscription.id}: {str(e)}', exc_info=True)
            
            # Mostrar estadísticas finales
            self.stdout.write(self.style.SUCCESS('\n📊 ESTADÍSTICAS FINALES:'))
            self.stdout.write(f'  📋 Suscripciones procesadas: {stats["processed"]}')
            self.stdout.write(f'  🔄 Cambios de estado: {stats["changed"]}')
            self.stdout.write(f'  ❌ Errores: {stats["errors"]}')
            self.stdout.write(f'  ⏰ Nuevas expiraciones: {stats["expired"]}')
            self.stdout.write(f'  🕐 Entradas en gracia: {stats["grace_period"]}')
            self.stdout.write(f'  ✅ Reactivaciones: {stats["reactivated"]}')
            
            # Detalles de cambios de estado
            if stats['status_changes']:
                self.stdout.write('\n🔄 CAMBIOS DE ESTADO:')
                for change, count in stats['status_changes'].items():
                    self.stdout.write(f'  {change}: {count} suscripciones')
            
            # Recomendaciones
            self.stdout.write('\n💡 RECOMENDACIONES:')
            
            if stats['expired'] > 0:
                self.stdout.write(f'  📧 Considerar enviar notificaciones de expiración a {stats["expired"]} organizaciones')
            
            if stats['grace_period'] > 0:
                self.stdout.write(f'  ⚠️  Hay {stats["grace_period"]} organizaciones en período de gracia')
            
            if stats['errors'] > 0:
                self.stdout.write(f'  🔧 Revisar {stats["errors"]} errores en los logs')
            
            if stats['changed'] == 0:
                self.stdout.write('  ✅ Todo está actualizado')
            
            # Próximas expiraciones (próximos 7 días)
            upcoming_expirations = self._get_upcoming_expirations()
            if upcoming_expirations:
                self.stdout.write(f'\n⏰ PRÓXIMAS EXPIRACIONES (7 días):')
                for exp in upcoming_expirations[:5]:  # Mostrar solo las primeras 5
                    days_remaining = (exp['end_date'] - timezone.now().date()).days
                    self.stdout.write(f'  📅 {exp["organization"]} - {days_remaining} días ({exp["plan"]})')
                
                if len(upcoming_expirations) > 5:
                    self.stdout.write(f'  ... y {len(upcoming_expirations) - 5} más')
            
            success_message = f'✅ Proceso completado: {stats["changed"]} cambios de estado'
            if dry_run:
                success_message += ' (DRY-RUN)'
            
            self.stdout.write(self.style.SUCCESS(f'\n{success_message}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error crítico: {str(e)}'))
            logger.error(f'Error crítico en actualización de estados: {str(e)}', exc_info=True)
            raise
    
    def _get_upcoming_expirations(self):
        """Obtiene suscripciones que expiran en los próximos 7 días"""
        try:
            from datetime import date, timedelta
            
            today = timezone.now().date()
            next_week = today + timedelta(days=7)
            
            subscriptions = Subscription.objects.filter(
                end_date__date__gte=today,
                end_date__date__lte=next_week,
                subscription_status__endswith='_active'
            ).select_related('organization', 'plan')
            
            return [
                {
                    'organization': sub.organization.name,
                    'plan': sub.plan.display_name,
                    'end_date': sub.end_date.date(),
                    'status': sub.subscription_status
                }
                for sub in subscriptions
            ]
        except Exception as e:
            logger.error(f'Error obteniendo próximas expiraciones: {str(e)}')
            return [] 