from django.core.management.base import BaseCommand
from apps.plans.models import Plan
from apps.orgs.models import Organization

class Command(BaseCommand):
    help = 'Asignar planes a organizaciones existentes'

    def handle(self, *args, **options):
        try:
            plan_gratuito = Plan.objects.get(name='gratuito')
            plan_basico = Plan.objects.get(name='basico')
            
            orgs_sin_plan = Organization.objects.filter(plan__isnull=True)
            
            for org in orgs_sin_plan:
                # Si la organización tiene más de 1 usuario o su max_users > 1, asignar plan básico
                # De lo contrario, asignar plan gratuito
                if org.get_max_users() > 1 or org.get_user_count() > 1:
                    org.plan = plan_basico
                    self.stdout.write(
                        self.style.SUCCESS(f'Asignado plan básico a {org.name}')
                    )
                else:
                    org.plan = plan_gratuito
                    self.stdout.write(
                        self.style.SUCCESS(f'Asignado plan gratuito a {org.name}')
                    )
                org.save()
            
            if not orgs_sin_plan.exists():
                self.stdout.write(
                    self.style.WARNING('No hay organizaciones sin plan asignado')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Se asignaron planes a {orgs_sin_plan.count()} organizaciones')
                )
                
        except Plan.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Error: Los planes por defecto no existen. Ejecuta create_default_plans primero.')
            ) 