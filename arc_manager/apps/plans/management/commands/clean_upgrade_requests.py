from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.plans.models import UpgradeRequest

class Command(BaseCommand):
    help = 'Limpia solicitudes de upgrade antiguas para mantener la base de datos limpia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días después de los cuales las solicitudes aprobadas/rechazadas se marcan como completadas (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué se haría, sin hacer cambios'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'=== LIMPIEZA DE SOLICITUDES DE UPGRADE ==='))
        self.stdout.write(f'Buscando solicitudes aprobadas/rechazadas desde antes del {cutoff_date.strftime("%d/%m/%Y")}')
        
        # Buscar solicitudes aprobadas antiguas
        approved_requests = UpgradeRequest.objects.filter(
            status='approved',
            approved_date__lt=cutoff_date
        )
        
        # Buscar solicitudes rechazadas antiguas
        rejected_requests = UpgradeRequest.objects.filter(
            status='rejected',
            approved_date__lt=cutoff_date
        )
        
        # Buscar solicitudes canceladas antiguas
        cancelled_requests = UpgradeRequest.objects.filter(
            status='cancelled',
            requested_date__lt=cutoff_date
        )
        
        total_approved = approved_requests.count()
        total_rejected = rejected_requests.count()
        total_cancelled = cancelled_requests.count()
        total_requests = total_approved + total_rejected + total_cancelled
        
        self.stdout.write(f'Solicitudes aprobadas antiguas: {total_approved}')
        self.stdout.write(f'Solicitudes rechazadas antiguas: {total_rejected}')
        self.stdout.write(f'Solicitudes canceladas antiguas: {total_cancelled}')
        self.stdout.write(f'Total a procesar: {total_requests}')
        
        if total_requests == 0:
            self.stdout.write(self.style.SUCCESS('✅ No hay solicitudes antiguas para limpiar'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN - Solo mostrando qué se haría:'))
            
            for request in approved_requests:
                self.stdout.write(f'  - Marcaría como completada: {request.organization.name} → {request.requested_plan.display_name} (aprobada el {request.approved_date.strftime("%d/%m/%Y")})')
            
            for request in rejected_requests:
                self.stdout.write(f'  - Marcaría como completada: {request.organization.name} → {request.requested_plan.display_name} (rechazada el {request.approved_date.strftime("%d/%m/%Y")})')
            
            for request in cancelled_requests:
                self.stdout.write(f'  - Marcaría como completada: {request.organization.name} → {request.requested_plan.display_name} (cancelada el {request.requested_date.strftime("%d/%m/%Y")})')
            
            self.stdout.write(self.style.WARNING('Para ejecutar los cambios, ejecuta sin --dry-run'))
            return
        
        # Marcar como completadas (esto las excluirá de las búsquedas futuras)
        updated_approved = approved_requests.update(status='completed')
        updated_rejected = rejected_requests.update(status='completed')
        updated_cancelled = cancelled_requests.update(status='completed')
        
        total_updated = updated_approved + updated_rejected + updated_cancelled
        
        self.stdout.write(self.style.SUCCESS(f'✅ Se marcaron como completadas {total_updated} solicitudes'))
        
        # Mostrar estadísticas finales
        self.stdout.write('\n=== ESTADÍSTICAS FINALES ===')
        
        pending_count = UpgradeRequest.objects.filter(status='pending').count()
        approved_recent = UpgradeRequest.objects.filter(
            status='approved',
            approved_date__gte=cutoff_date
        ).count()
        completed_count = UpgradeRequest.objects.filter(status='completed').count()
        
        self.stdout.write(f'Solicitudes pendientes: {pending_count}')
        self.stdout.write(f'Solicitudes aprobadas recientes (últimos {days} días): {approved_recent}')
        self.stdout.write(f'Solicitudes completadas (archivadas): {completed_count}')
        
        if pending_count == 0 and approved_recent == 0:
            self.stdout.write(self.style.SUCCESS('✅ No hay solicitudes activas. El sistema está limpio.'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Hay {pending_count + approved_recent} solicitudes activas')) 