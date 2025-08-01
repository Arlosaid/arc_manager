from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.plans.models import Plan, Subscription, Payment, UpgradeRequest
from apps.orgs.models import Organization
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Diagnostica y corrige problemas en el sistema de suscripciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Limpia automáticamente duplicados encontrados'
        )
        parser.add_argument(
            '--fix-inconsistencies',
            action='store_true',
            help='Corrige inconsistencias automáticamente'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando diagnóstico del sistema de suscripciones'))
        
        # Estadísticas generales
        self.show_general_stats()
        
        # Verificar planes
        self.check_plans()
        
        # Verificar suscripciones
        self.check_subscriptions(options['fix_inconsistencies'])
        
        # Verificar pagos duplicados
        self.check_duplicate_payments(options['clean'])
        
        # Verificar solicitudes de upgrade
        self.check_upgrade_requests()
        
        self.stdout.write(self.style.SUCCESS('✅ Diagnóstico completado'))

    def show_general_stats(self):
        """Muestra estadísticas generales del sistema"""
        self.stdout.write('\n📊 ESTADÍSTICAS GENERALES')
        self.stdout.write('-' * 50)
        
        # Contar por tipo
        organizations = Organization.objects.count()
        subscriptions = Subscription.objects.count()
        payments = Payment.objects.count()
        upgrade_requests = UpgradeRequest.objects.count()
        
        self.stdout.write(f'Organizations: {organizations}')
        self.stdout.write(f'Subscriptions: {subscriptions}')
        self.stdout.write(f'Payments: {payments}')
        self.stdout.write(f'Upgrade Requests: {upgrade_requests}')
        
        # Estados de suscripciones
        self.stdout.write('\n📈 ESTADOS DE SUSCRIPCIONES')
        status_counts = {}
        for subscription in Subscription.objects.all():
            status = subscription.subscription_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            self.stdout.write(f'  {status}: {count}')

    def check_plans(self):
        """Verifica la configuración de planes"""
        self.stdout.write('\n🎯 VERIFICACIÓN DE PLANES')
        self.stdout.write('-' * 50)
        
        plans = Plan.objects.all()
        
        if not plans.exists():
            self.stdout.write(self.style.ERROR('❌ No hay planes configurados'))
            return
        
        trial_plan = Plan.get_trial_plan()
        basic_plan = Plan.get_basic_plan()
        
        if not trial_plan:
            self.stdout.write(self.style.WARNING('⚠️  No hay plan trial configurado'))
        else:
            self.stdout.write(f'✅ Plan trial: {trial_plan.display_name}')
        
        if not basic_plan:
            self.stdout.write(self.style.WARNING('⚠️  No hay plan básico configurado'))
        else:
            self.stdout.write(f'✅ Plan básico: {basic_plan.display_name}')
        
        # Verificar configuración de planes
        for plan in plans:
            issues = []
            
            if plan.name == 'trial' and plan.trial_days == 0:
                issues.append('trial_days debe ser > 0')
            
            if plan.name == 'basic' and plan.grace_period_days == 0:
                issues.append('grace_period_days debe ser > 0')
            
            if issues:
                self.stdout.write(self.style.WARNING(f'⚠️  Plan {plan.display_name}: {", ".join(issues)}'))

    def check_subscriptions(self, fix_inconsistencies=False):
        """Verifica y corrige inconsistencias en suscripciones"""
        self.stdout.write('\n📋 VERIFICACIÓN DE SUSCRIPCIONES')
        self.stdout.write('-' * 50)
        
        # Organizaciones sin suscripción
        orgs_without_subscription = Organization.objects.filter(subscription__isnull=True)
        if orgs_without_subscription.exists():
            self.stdout.write(f'⚠️  {orgs_without_subscription.count()} organizaciones sin suscripción')
            
            if fix_inconsistencies:
                from apps.plans.services import SubscriptionService
                fixed = 0
                for org in orgs_without_subscription:
                    result = SubscriptionService.create_trial_subscription(org)
                    if result['success']:
                        fixed += 1
                
                self.stdout.write(self.style.SUCCESS(f'✅ Se crearon {fixed} suscripciones trial'))
        
        # Verificar estados inconsistentes
        inconsistent_subscriptions = []
        for subscription in Subscription.objects.all():
            current_status = subscription.subscription_status
            calculated_status = subscription.calculate_current_status()
            
            if current_status != calculated_status:
                inconsistent_subscriptions.append((subscription, current_status, calculated_status))
        
        if inconsistent_subscriptions:
            self.stdout.write(f'⚠️  {len(inconsistent_subscriptions)} suscripciones con estado inconsistente')
            
            for subscription, current, calculated in inconsistent_subscriptions[:5]:  # Solo mostrar las primeras 5
                self.stdout.write(f'  {subscription.organization.name}: {current} → {calculated}')
            
            if fix_inconsistencies:
                fixed = 0
                with transaction.atomic():
                    for subscription, current, calculated in inconsistent_subscriptions:
                        subscription.subscription_status = calculated
                        subscription.save()
                        fixed += 1
                
                self.stdout.write(self.style.SUCCESS(f'✅ Se corrigieron {fixed} estados inconsistentes'))

    def check_duplicate_payments(self, clean_duplicates=False):
        """Verifica y limpia pagos duplicados"""
        self.stdout.write('\n💰 VERIFICACIÓN DE PAGOS')
        self.stdout.write('-' * 50)
        
        # Buscar duplicados por suscripción, monto y fecha (mismo día)
        from django.db.models import Count
        from datetime import date
        
        duplicates_found = 0
        duplicates_cleaned = 0
        
        for subscription in Subscription.objects.all():
            payments_by_date = {}
            
            for payment in subscription.payments.filter(status='completed'):
                payment_date = payment.payment_date.date()
                key = (payment_date, float(payment.amount))
                
                if key not in payments_by_date:
                    payments_by_date[key] = []
                payments_by_date[key].append(payment)
            
            # Identificar duplicados
            for key, payments in payments_by_date.items():
                if len(payments) > 1:
                    duplicates_found += len(payments) - 1
                    
                    if clean_duplicates:
                        # Mantener el primer pago, eliminar los duplicados
                        payments_to_delete = payments[1:]
                        for payment in payments_to_delete:
                            payment.delete()
                            duplicates_cleaned += 1
        
        if duplicates_found > 0:
            self.stdout.write(f'⚠️  Se encontraron {duplicates_found} pagos duplicados')
            if clean_duplicates:
                self.stdout.write(self.style.SUCCESS(f'✅ Se eliminaron {duplicates_cleaned} pagos duplicados'))
        else:
            self.stdout.write('✅ No se encontraron pagos duplicados')

    def check_upgrade_requests(self):
        """Verifica solicitudes de upgrade"""
        self.stdout.write('\n🚀 VERIFICACIÓN DE SOLICITUDES DE UPGRADE')
        self.stdout.write('-' * 50)
        
        # Contar por estado
        status_counts = {}
        for request in UpgradeRequest.objects.all():
            status = request.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            self.stdout.write(f'  {status}: {count}')
        
        # Solicitudes muy antiguas pendientes
        old_pending = UpgradeRequest.objects.filter(
            status='pending',
            created_at__lt=timezone.now() - timezone.timedelta(days=30)
        )
        
        if old_pending.exists():
            self.stdout.write(f'⚠️  {old_pending.count()} solicitudes pendientes de más de 30 días')
            for request in old_pending[:3]:  # Mostrar solo las primeras 3
                self.stdout.write(f'  {request.organization.name}: {request.created_at.date()}') 