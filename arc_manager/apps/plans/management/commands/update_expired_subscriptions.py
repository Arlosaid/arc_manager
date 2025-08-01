from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.plans.models import Subscription
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualiza automáticamente el estado de todas las suscripciones expiradas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando sin hacer cambios reales (solo simula)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada del proceso',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: No se realizarán cambios reales'))
        
        self.stdout.write('🔄 Actualizando estado de suscripciones...')
        
        # Obtener todas las suscripciones que no están expiradas
        subscriptions = Subscription.objects.exclude(
            subscription_status__in=['trial_expired', 'basic_expired']
        )
        
        total_subscriptions = subscriptions.count()
        updated_count = 0
        
        self.stdout.write(f'📊 Verificando {total_subscriptions} suscripciones...')
        
        for subscription in subscriptions:
            old_status = subscription.subscription_status
            
            if verbose:
                self.stdout.write(f'   • {subscription.organization.name} ({old_status})')

            # Simular la actualización de estado si es dry-run
            if dry_run:
                new_status = subscription.calculate_current_status()
            else:
                subscription.update_status()
                new_status = subscription.subscription_status
            
            if old_status != new_status:
                updated_count += 1
                
                if 'expired' in new_status:
                    status_color = self.style.ERROR
                    status_icon = '❌'
                elif 'grace' in new_status:
                    status_color = self.style.WARNING
                    status_icon = '⏳'
                else:
                    status_color = self.style.SUCCESS
                    status_icon = '✅'
                
                self.stdout.write(
                    f'   {status_icon} {subscription.organization.name}: {old_status} → {status_color(new_status)}'
                )
                
                if verbose:
                    end_date_str = subscription.end_date.strftime("%d/%m/%Y") if subscription.end_date else "N/A"
                    self.stdout.write(f'      Fecha de vencimiento: {end_date_str}')
        
        # Resumen
        self.stdout.write('')
        self.stdout.write(f'📋 Resumen:')
        self.stdout.write(f'   • Total verificadas: {total_subscriptions}')
        self.stdout.write(f'   • Actualizadas: {updated_count}')
        self.stdout.write(f'   • Sin cambios: {total_subscriptions - updated_count}')
        
        if updated_count > 0:
            if dry_run:
                self.stdout.write(self.style.WARNING(f'⚠️  {updated_count} suscripciones necesitan actualizarse (simulado)'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ {updated_count} suscripciones actualizadas correctamente'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Todas las suscripciones están al día'))
        
        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('💡 Para aplicar los cambios, ejecuta el comando sin --dry-run')) 