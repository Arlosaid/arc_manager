from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.plans.models import Plan, UpgradeRequest, Subscription
from apps.orgs.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Diagnostica el estado de las solicitudes de upgrade'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            type=str,
            help='Nombre de la organización a revisar'
        )
        parser.add_argument(
            '--create-test',
            action='store_true',
            help='Crear una solicitud de prueba'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Limpiar solicitudes de prueba'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Diagnóstico de Solicitudes de Upgrade'))
        self.stdout.write('=' * 50)
        
        # 1. Verificar estado general
        self.stdout.write('\n📊 ESTADO GENERAL:')
        total_requests = UpgradeRequest.objects.count()
        pending_requests = UpgradeRequest.objects.filter(status='pending').count()
        approved_requests = UpgradeRequest.objects.filter(status='approved').count()
        
        self.stdout.write(f'  Total de solicitudes: {total_requests}')
        self.stdout.write(f'  Solicitudes pendientes: {pending_requests}')
        self.stdout.write(f'  Solicitudes aprobadas: {approved_requests}')
        
        # 2. Listar todas las solicitudes
        self.stdout.write('\n📋 TODAS LAS SOLICITUDES:')
        for request in UpgradeRequest.objects.all().order_by('-requested_date'):
            self.stdout.write(f'  ID: {request.id}')
            self.stdout.write(f'    Organización: {request.organization.name}')
            self.stdout.write(f'    Usuario: {request.requested_by.email}')
            self.stdout.write(f'    Plan: {request.current_plan.display_name} → {request.requested_plan.display_name}')
            self.stdout.write(f'    Estado: {request.status}')
            self.stdout.write(f'    Fecha: {request.requested_date}')
            self.stdout.write(f'    Monto: ${request.amount_due}')
            self.stdout.write('')
        
        # 3. Verificar organización específica
        if options['organization']:
            self.stdout.write(f'\n🏢 ORGANIZACIÓN: {options["organization"]}')
            try:
                org = Organization.objects.get(name__icontains=options['organization'])
                self.stdout.write(f'  Encontrada: {org.name}')
                
                # Verificar suscripción
                try:
                    subscription = org.subscription
                    self.stdout.write(f'  Plan actual: {subscription.plan.display_name}')
                    self.stdout.write(f'  Estado: {subscription.status}')
                    
                    # Verificar solicitudes de esta organización
                    org_requests = UpgradeRequest.objects.filter(organization=org)
                    self.stdout.write(f'  Solicitudes de esta org: {org_requests.count()}')
                    
                    for req in org_requests:
                        self.stdout.write(f'    - ID {req.id}: {req.status} ({req.requested_date})')
                        
                except Exception as e:
                    self.stdout.write(f'  ❌ Error con suscripción: {e}')
                    
            except Organization.DoesNotExist:
                self.stdout.write(f'  ❌ No se encontró organización con nombre que contenga: {options["organization"]}')
                
                # Mostrar organizaciones disponibles
                self.stdout.write('\n📌 Organizaciones disponibles:')
                for org in Organization.objects.all():
                    self.stdout.write(f'  - {org.name}')
        
        # 4. Crear solicitud de prueba
        if options['create_test']:
            self.stdout.write('\n🧪 CREANDO SOLICITUD DE PRUEBA:')
            
            # Buscar primera organización con suscripción
            for org in Organization.objects.all():
                try:
                    subscription = org.subscription
                    current_plan = subscription.plan
                    
                    # Buscar un plan superior
                    higher_plan = Plan.objects.filter(
                        is_active=True, 
                        price__gt=current_plan.price
                    ).first()
                    
                    if higher_plan:
                        # Buscar un admin de la organización
                        admin_user = org.users.filter(is_org_admin=True).first()
                        if admin_user:
                            # Crear solicitud de prueba
                            test_request = UpgradeRequest.objects.create(
                                organization=org,
                                current_plan=current_plan,
                                requested_plan=higher_plan,
                                requested_by=admin_user,
                                amount_due=higher_plan.price - current_plan.price,
                                request_notes="Solicitud de prueba creada por comando de diagnóstico"
                            )
                            
                            self.stdout.write(f'  ✅ Solicitud de prueba creada:')
                            self.stdout.write(f'    ID: {test_request.id}')
                            self.stdout.write(f'    Organización: {org.name}')
                            self.stdout.write(f'    Plan: {current_plan.display_name} → {higher_plan.display_name}')
                            self.stdout.write(f'    Usuario: {admin_user.email}')
                            break
                        else:
                            self.stdout.write(f'  ⚠️ {org.name} no tiene admins')
                    else:
                        self.stdout.write(f'  ⚠️ {org.name} ya tiene el plan más alto')
                        
                except Exception as e:
                    self.stdout.write(f'  ❌ Error con {org.name}: {e}')
                    continue
            else:
                self.stdout.write('  ❌ No se pudo crear solicitud de prueba')
        
        # 5. Limpiar solicitudes de prueba
        if options['cleanup']:
            self.stdout.write('\n🧹 LIMPIANDO SOLICITUDES DE PRUEBA:')
            test_requests = UpgradeRequest.objects.filter(
                request_notes__icontains='prueba'
            )
            count = test_requests.count()
            test_requests.delete()
            self.stdout.write(f'  ✅ Eliminadas {count} solicitudes de prueba')
        
        # 6. Verificar configuración del admin
        self.stdout.write('\n⚙️ CONFIGURACIÓN:')
        self.stdout.write(f'  Planes activos: {Plan.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  Organizaciones: {Organization.objects.count()}')
        self.stdout.write(f'  Suscripciones: {Subscription.objects.count()}')
        
        # 7. Sugerencias
        self.stdout.write('\n💡 SUGERENCIAS:')
        if total_requests == 0:
            self.stdout.write('  - No hay solicitudes. Usa --create-test para crear una de prueba')
        if pending_requests > 0:
            self.stdout.write(f'  - Hay {pending_requests} solicitudes pendientes en el admin')
        
        self.stdout.write('\n✅ Diagnóstico completado') 