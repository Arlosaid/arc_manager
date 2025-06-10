from django.core.management.base import BaseCommand
from django.db.models import Count, Q, F
from django.db import models
from apps.orgs.models import Organization
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Validar integridad de datos multitenant'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corregir automáticamente problemas encontrados',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostrar información detallada de todas las organizaciones',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🔍 Validando datos multitenant...\n')
        
        # Contadores de problemas
        problems_found = 0
        problems_fixed = 0
        
        # 1. Verificar organizaciones sin suscripción
        self.stdout.write(self.style.HTTP_INFO('📋 Verificando suscripciones...'))
        orgs_no_sub = Organization.objects.filter(subscription__isnull=True)
        if orgs_no_sub.exists():
            problems_found += orgs_no_sub.count()
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {orgs_no_sub.count()} organizaciones sin suscripción:'
                )
            )
            for org in orgs_no_sub:
                self.stdout.write(f'   - {org.name} (ID: {org.id})')
                if options['fix']:
                    # Crear suscripción trial por defecto
                    sub = org._create_default_subscription()
                    if sub:
                        problems_fixed += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'     ✅ Suscripción trial creada')
                        )
        else:
            self.stdout.write(self.style.SUCCESS('✅ Todas las organizaciones tienen suscripción'))
        
        # 2. Verificar usuarios sin organización activos
        self.stdout.write(self.style.HTTP_INFO('\n👥 Verificando usuarios sin organización...'))
        users_no_org = User.objects.filter(
            organization__isnull=True, 
            is_active=True, 
            is_superuser=False
        )
        if users_no_org.exists():
            problems_found += users_no_org.count()
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {users_no_org.count()} usuarios activos sin organización:'
                )
            )
            for user in users_no_org:
                self.stdout.write(f'   - {user.email} ({user.get_full_name() or "Sin nombre"})')
                if options['fix']:
                    # Desactivar usuarios sin organización
                    user.is_active = False
                    user.save()
                    problems_fixed += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'     ✅ Usuario desactivado')
                    )
        else:
            self.stdout.write(self.style.SUCCESS('✅ Todos los usuarios activos tienen organización'))
        
        # 3. Verificar usuarios con username duplicado o problemático
        self.stdout.write(self.style.HTTP_INFO('\n🏷️  Verificando nombres de usuario...'))
        
        # Usuarios con username igual al email
        users_username_email = User.objects.filter(username=F('email')).exclude(username__isnull=True)
        if users_username_email.exists():
            problems_found += users_username_email.count()
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {users_username_email.count()} usuarios con username = email:'
                )
            )
            for user in users_username_email[:5]:  # Mostrar solo primeros 5
                self.stdout.write(f'   - {user.email}')
            if users_username_email.count() > 5:
                self.stdout.write(f'   ... y {users_username_email.count() - 5} más')
        
        # Usuarios con username vacío
        users_no_username = User.objects.filter(Q(username__isnull=True) | Q(username=''))
        if users_no_username.exists():
            problems_found += users_no_username.count()
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {users_no_username.count()} usuarios sin username:'
                )
            )
            for user in users_no_username[:5]:
                self.stdout.write(f'   - {user.email}')
            if users_no_username.count() > 5:
                self.stdout.write(f'   ... y {users_no_username.count() - 5} más')
        
        # 4. Verificar límites excedidos
        self.stdout.write(self.style.HTTP_INFO('\n📊 Verificando límites de usuarios...'))
        limit_violations = 0
        
        for org in Organization.objects.all():
            try:
                max_users = org.get_max_users()
                current_users = org.users.filter(is_active=True).count()
                total_users = org.users.count()
                
                if current_users > max_users:
                    limit_violations += 1
                    problems_found += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ {org.name}: {current_users}/{max_users} usuarios activos (límite excedido)'
                        )
                    )
                    if total_users > current_users:
                        self.stdout.write(f'   Total (incluyendo inactivos): {total_users}')
                elif options['detailed']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ {org.name}: {current_users}/{max_users} usuarios activos'
                        )
                    )
                    if total_users > current_users:
                        self.stdout.write(f'   Total (incluyendo inactivos): {total_users}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error verificando {org.name}: {str(e)}')
                )
        
        if limit_violations == 0:
            self.stdout.write(self.style.SUCCESS('✅ Todas las organizaciones respetan sus límites'))
        
        # 5. Verificar orphaned admin flags
        self.stdout.write(self.style.HTTP_INFO('\n👑 Verificando flags de administrador...'))
        
        # Admins sin organización
        orphaned_admins = User.objects.filter(
            is_org_admin=True,
            organization__isnull=True,
            is_superuser=False
        )
        if orphaned_admins.exists():
            problems_found += orphaned_admins.count()
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {orphaned_admins.count()} usuarios marcados como admin sin organización:'
                )
            )
            for admin in orphaned_admins:
                self.stdout.write(f'   - {admin.email}')
                if options['fix']:
                    admin.is_org_admin = False
                    admin.save()
                    problems_fixed += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'     ✅ Flag de admin removido')
                    )
        else:
            self.stdout.write(self.style.SUCCESS('✅ Todos los admins tienen organización'))
        
        # 6. Resumen final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('📈 RESUMEN DE VALIDACIÓN'))
        self.stdout.write('='*60)
        
        if problems_found == 0:
            self.stdout.write(self.style.SUCCESS('🎉 ¡No se encontraron problemas! El sistema está bien configurado.'))
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Se encontraron {problems_found} problemas.')
            )
            if options['fix']:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Se corrigieron {problems_fixed} problemas automáticamente.')
                )
                remaining = problems_found - problems_fixed
                if remaining > 0:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {remaining} problemas requieren atención manual.')
                    )
            else:
                self.stdout.write(
                    self.style.HTTP_INFO('💡 Ejecuta con --fix para corregir automáticamente los problemas que se puedan resolver.')
                )
        
        # Estadísticas generales
        total_orgs = Organization.objects.count()
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        self.stdout.write('\n' + self.style.HTTP_INFO('📊 ESTADÍSTICAS GENERALES'))
        self.stdout.write(f'Organizaciones: {total_orgs}')
        self.stdout.write(f'Usuarios totales: {total_users}')
        self.stdout.write(f'Usuarios activos: {active_users}')
        self.stdout.write(f'Superusuarios: {User.objects.filter(is_superuser=True).count()}')
        self.stdout.write(f'Admins de org: {User.objects.filter(is_org_admin=True).count()}') 