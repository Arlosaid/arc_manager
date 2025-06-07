from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.plans.models import Plan, UpgradeRequest, Subscription
from apps.orgs.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba el sistema de upgrades completo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Iniciando prueba del sistema de upgrades...'))
        
        try:
            # 1. Verificar planes disponibles
            self.stdout.write('📋 Verificando planes...')
            plans = Plan.objects.all()
            for plan in plans:
                self.stdout.write(f'  - {plan.name}: {plan.display_name} (${plan.price})')
            
            # 2. Buscar una organización de prueba
            org = Organization.objects.first()
            if not org:
                self.stdout.write(self.style.ERROR('❌ No hay organizaciones en el sistema'))
                return
            
            self.stdout.write(f'🏢 Usando organización: {org.name}')
            
            # 3. Verificar suscripción
            try:
                subscription = org.subscription
                self.stdout.write(f'📋 Plan actual: {subscription.plan.display_name}')
            except:
                self.stdout.write(self.style.ERROR('❌ La organización no tiene suscripción'))
                return
            
            # 4. Buscar solicitudes de upgrade
            upgrade_requests = UpgradeRequest.objects.filter(organization=org)
            self.stdout.write(f'📄 Solicitudes encontradas: {upgrade_requests.count()}')
            
            for request in upgrade_requests:
                self.stdout.write(f'  - ID {request.id}: {request.status} | {request.current_plan.display_name} → {request.requested_plan.display_name}')
                
                # 5. Probar completar upgrade si hay alguna
                if request.status in ['pending', 'approved', 'payment_pending']:
                    self.stdout.write(f'🔄 Probando completar upgrade {request.id}...')
                    
                    # Buscar un superuser para usar como completed_by
                    admin_user = User.objects.filter(is_superuser=True).first()
                    if not admin_user:
                        self.stdout.write(self.style.ERROR('❌ No hay superusuarios'))
                        continue
                    
                    try:
                        # Probar el complete_upgrade directamente
                        old_plan = subscription.plan.display_name
                        result = request.complete_upgrade(completed_by_user=admin_user)
                        
                        # Verificar resultado
                        subscription.refresh_from_db()
                        new_plan = subscription.plan.display_name
                        
                        self.stdout.write(self.style.SUCCESS(f'✅ Upgrade completado!'))
                        self.stdout.write(f'   Plan cambió: {old_plan} → {new_plan}')
                        self.stdout.write(f'   Estado suscripción: {subscription.status}')
                        self.stdout.write(f'   Estado solicitud: {request.status}')
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Error al completar upgrade: {str(e)}'))
                        
                        # Información de debug
                        self.stdout.write(f'   Estado actual de la solicitud: {request.status}')
                        self.stdout.write(f'   Plan actual suscripción: {subscription.plan.display_name}')
                        self.stdout.write(f'   Plan solicitado: {request.requested_plan.display_name}')
                    
                    break  # Solo probar una
            
            # 6. Crear una solicitud de prueba si no hay ninguna
            if upgrade_requests.count() == 0:
                self.stdout.write('🆕 Creando solicitud de prueba...')
                
                # Buscar planes para upgrade
                current_plan = subscription.plan
                available_plans = Plan.objects.filter(price__gt=current_plan.price, is_active=True)
                
                if available_plans.exists():
                    target_plan = available_plans.first()
                    admin_user = User.objects.filter(is_superuser=True).first()
                    
                    if admin_user:
                        test_request = UpgradeRequest.objects.create(
                            organization=org,
                            current_plan=current_plan,
                            requested_plan=target_plan,
                            requested_by=admin_user,
                            amount_due=target_plan.price - current_plan.price,
                            request_notes="Solicitud de prueba creada por comando de test"
                        )
                        
                        self.stdout.write(f'✅ Solicitud creada: ID {test_request.id}')
                        self.stdout.write('🔄 Probando completar inmediatamente...')
                        
                        try:
                            old_plan = subscription.plan.display_name
                            test_request.complete_upgrade(completed_by_user=admin_user)
                            
                            subscription.refresh_from_db()
                            new_plan = subscription.plan.display_name
                            
                            self.stdout.write(self.style.SUCCESS('✅ ¡Prueba exitosa!'))
                            self.stdout.write(f'   Plan cambió: {old_plan} → {new_plan}')
                            
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'❌ Error en prueba: {str(e)}'))
                    else:
                        self.stdout.write(self.style.ERROR('❌ No hay superusuarios para la prueba'))
                else:
                    self.stdout.write('⚠️ No hay planes superiores disponibles para prueba')
            
            self.stdout.write(self.style.SUCCESS('🎉 Prueba del sistema completada'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'💥 Error general: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc()) 