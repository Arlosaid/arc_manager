from django.core.management.base import BaseCommand
from django.db import transaction
from apps.plans.models import Plan
import json

class Command(BaseCommand):
    help = 'Configura los planes básicos para el MVP con gestión manual'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Sobrescribir planes existentes',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        plans_config = [
            {
                'name': 'trial',
                'display_name': 'Prueba Gratuita',
                'description': 'Período de prueba de 30 días para probar todas las funciones básicas',
                'price': 0.00,
                'currency': 'MXN',
                'billing_cycle': 'trial',
                'max_users': 2,
                'max_projects': 3,
                'storage_limit_gb': 1,
                'trial_days': 30,
                'features': {
                    'features': [
                        'Acceso completo por 30 días',
                        'Hasta 2 usuarios',
                        'Hasta 3 proyectos',
                        '1 GB de almacenamiento',
                        'Soporte por email'
                    ]
                },
                'is_active': True,
                'is_featured': False,
                'sort_order': 1
            },
            {
                'name': 'basic',
                'display_name': 'Plan Básico',
                'description': 'Plan básico ideal para pequeños equipos que inician',
                'price': 299.00,
                'currency': 'MXN',
                'billing_cycle': 'monthly',
                'max_users': 5,
                'max_projects': 10,
                'storage_limit_gb': 5,
                'trial_days': 0,
                'features': {
                    'features': [
                        'Hasta 5 usuarios',
                        'Hasta 10 proyectos',
                        '5 GB de almacenamiento',
                        'Soporte por email',
                        'Respaldos diarios',
                        'Sin anuncios'
                    ]
                },
                'is_active': True,
                'is_featured': True,
                'sort_order': 2
            },
            {
                'name': 'premium',
                'display_name': 'Plan Premium',
                'description': 'Plan premium para equipos en crecimiento con necesidades avanzadas',
                'price': 599.00,
                'currency': 'MXN',
                'billing_cycle': 'monthly',
                'max_users': 15,
                'max_projects': 50,
                'storage_limit_gb': 20,
                'trial_days': 0,
                'features': {
                    'features': [
                        'Hasta 15 usuarios',
                        'Hasta 50 proyectos',
                        '20 GB de almacenamiento',
                        'Soporte prioritario',
                        'Respaldos diarios',
                        'Reportes avanzados',
                        'Integraciones API',
                        'Sin anuncios'
                    ]
                },
                'is_active': True,
                'is_featured': False,
                'sort_order': 3
            }
        ]

        self.stdout.write("🚀 Configurando planes para MVP...")
        
        with transaction.atomic():
            created_count = 0
            updated_count = 0
            
            for plan_data in plans_config:
                plan_name = plan_data['name']
                
                try:
                    plan, created = Plan.objects.get_or_create(
                        name=plan_name,
                        defaults=plan_data
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Creado: {plan.display_name}")
                        )
                    elif force:
                        # Actualizar plan existente
                        for key, value in plan_data.items():
                            setattr(plan, key, value)
                        plan.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"🔄 Actualizado: {plan.display_name}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️  Ya existe: {plan.display_name} (usa --force para actualizar)")
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error creando {plan_name}: {str(e)}")
                    )

        # Mostrar resumen
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN DE CONFIGURACIÓN"))
        self.stdout.write("="*50)
        
        if created_count > 0:
            self.stdout.write(f"✅ Planes creados: {created_count}")
        if updated_count > 0:
            self.stdout.write(f"🔄 Planes actualizados: {updated_count}")
            
        # Mostrar planes activos
        active_plans = Plan.objects.filter(is_active=True).order_by('sort_order')
        self.stdout.write(f"\n📋 Planes activos ({active_plans.count()}):")
        
        for plan in active_plans:
            price_display = f"${plan.price:,.0f} MXN/mes" if plan.price > 0 else "Gratis"
            featured = " ⭐" if plan.is_featured else ""
            self.stdout.write(f"  • {plan.display_name} - {price_display}{featured}")
            self.stdout.write(f"    👥 {plan.max_users} usuarios | 📁 {plan.max_projects} proyectos | 💾 {plan.storage_limit_gb} GB")

        # Instrucciones post-configuración
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📝 PRÓXIMOS PASOS PARA TU MVP"))
        self.stdout.write("="*50)
        
        instructions = [
            "1. Ve al admin Django (/admin) para ajustar precios si es necesario",
            "2. Configura tus métodos de pago manual en las vistas",
            "3. Actualiza la información de contacto en los templates",
            "4. Prueba el flujo completo: registro → trial → upgrade manual",
            "5. Configura emails para notificaciones de pagos",
            "",
            "💡 URLs importantes:",
            "   • Panel de gestión: /plans/admin/subscriptions/",
            "   • Admin Django: /admin/plans/",
            "   • Vista pública: /plans/pricing/",
            "",
            "🔧 Para crear planes adicionales, edita este comando o usa el admin Django"
        ]
        
        for instruction in instructions:
            if instruction.startswith("💡") or instruction.startswith("🔧"):
                self.stdout.write(self.style.WARNING(instruction))
            elif instruction.startswith("   •"):
                self.stdout.write(f"     {instruction[4:]}")
            else:
                self.stdout.write(instruction)
                
        self.stdout.write(f"\n🎉 ¡Configuración completada! Tu MVP está listo para gestión manual de pagos.") 