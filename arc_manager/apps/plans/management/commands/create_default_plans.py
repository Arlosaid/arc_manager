from django.core.management.base import BaseCommand
from apps.plans.models import Plan

class Command(BaseCommand):
    help = 'Crear planes por defecto del sistema'

    def handle(self, *args, **options):
        # Crear plan gratuito
        plan_gratuito, created = Plan.objects.get_or_create(
            name='gratuito',
            defaults={
                'display_name': 'Plan Gratuito',
                'description': 'Plan básico gratuito con 1 usuario',
                'max_users': 1,
                'price': 0,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Plan gratuito creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Plan gratuito ya existe')
            )
        
        # Crear plan básico
        plan_basico, created = Plan.objects.get_or_create(
            name='basico',
            defaults={
                'display_name': 'Plan Básico',
                'description': 'Plan básico con hasta 4 usuarios',
                'max_users': 4,
                'price': 9.99,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Plan básico creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Plan básico ya existe')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Operación completada exitosamente')
        ) 