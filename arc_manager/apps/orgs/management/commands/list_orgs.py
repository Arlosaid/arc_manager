from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.orgs.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Listar organizaciones y usuarios del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostrar información detallada de usuarios'
        )
        parser.add_argument(
            '--org-slug',
            type=str,
            help='Mostrar solo una organización específica'
        )
        parser.add_argument(
            '--users-only',
            action='store_true',
            help='Mostrar solo usuarios sin organización'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        org_slug = options['org_slug']
        users_only = options['users_only']

        if users_only:
            self.show_unassigned_users(detailed)
            return

        if org_slug:
            try:
                org = Organization.objects.get(slug=org_slug)
                self.show_organization_detail(org, detailed)
            except Organization.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'No existe una organización con slug "{org_slug}"')
                )
            return

        # Mostrar resumen general
        total_orgs = Organization.objects.count()
        total_users = User.objects.count()
        users_with_org = User.objects.filter(organization__isnull=False).count()
        users_without_org = total_users - users_with_org

        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DEL SISTEMA'))
        self.stdout.write('=' * 50)
        self.stdout.write(f'🏢 Organizaciones totales: {total_orgs}')
        self.stdout.write(f'👥 Usuarios totales: {total_users}')
        self.stdout.write(f'✅ Usuarios asignados: {users_with_org}')
        self.stdout.write(f'❌ Usuarios sin organización: {users_without_org}')
        self.stdout.write('')

        # Listar organizaciones
        organizations = Organization.objects.all().order_by('name')
        
        if not organizations:
            self.stdout.write(self.style.WARNING('No hay organizaciones registradas.'))
            return

        for org in organizations:
            self.show_organization_summary(org, detailed)

        # Mostrar usuarios sin organización si los hay
        if users_without_org > 0:
            self.stdout.write(self.style.WARNING('\n👤 USUARIOS SIN ORGANIZACIÓN'))
            self.stdout.write('-' * 30)
            unassigned_users = User.objects.filter(organization__isnull=True)
            for user in unassigned_users:
                role = "Superusuario" if user.is_superuser else "Usuario"
                status = "✅" if user.is_active else "❌"
                self.stdout.write(f'  {status} {user.username} ({user.email}) - {role}')

    def show_organization_summary(self, org, detailed=False):
        """Mostrar resumen de una organización"""
        status_icon = "✅" if org.is_active else "❌"
        user_count = org.get_user_count()
        admin_count = org.get_admins().count()
        
        self.stdout.write(f'\n{status_icon} {org.name} (slug: {org.slug})')
        self.stdout.write(f'   📝 {org.description or "Sin descripción"}')
        self.stdout.write(f'   👥 Usuarios: {user_count}/{org.get_max_users()}')
        self.stdout.write(f'   👑 Administradores: {admin_count}')
        
        if detailed and user_count > 0:
            self.stdout.write('   📋 Usuarios:')
            for user in org.users.all():
                role = "👑 Admin" if user.is_org_admin else "👤 Usuario"
                status = "✅" if user.is_active else "❌"
                last_login = user.last_login.strftime('%d/%m/%Y') if user.last_login else 'Nunca'
                self.stdout.write(f'      {status} {role} - {user.username} ({user.email}) - Último acceso: {last_login}')

    def show_organization_detail(self, org, detailed=False):
        """Mostrar detalles completos de una organización"""
        status = "Activa" if org.is_active else "Inactiva"
        
        self.stdout.write(self.style.SUCCESS(f'🏢 {org.name}'))
        self.stdout.write('=' * 50)
        self.stdout.write(f'📝 Descripción: {org.description or "Sin descripción"}')
        self.stdout.write(f'🔗 Slug: {org.slug}')
        self.stdout.write(f'📊 Estado: {status}')
        self.stdout.write(f'👥 Usuarios: {org.get_user_count()}/{org.get_max_users()}')
        self.stdout.write(f'📅 Creada: {org.created_at.strftime("%d/%m/%Y %H:%M")}')
        self.stdout.write(f'🔄 Actualizada: {org.updated_at.strftime("%d/%m/%Y %H:%M")}')
        
        users = org.users.all()
        if users:
            self.stdout.write(f'\n👥 USUARIOS ({users.count()}):')
            self.stdout.write('-' * 30)
            
            for user in users:
                role_icon = "👑" if user.is_org_admin else "👤"
                status_icon = "✅" if user.is_active else "❌"
                role_text = "Administrador" if user.is_org_admin else "Usuario"
                
                self.stdout.write(f'{status_icon} {role_icon} {user.username}')
                self.stdout.write(f'   📧 Email: {user.email}')
                self.stdout.write(f'   🎭 Rol: {role_text}')
                
                if detailed:
                    last_login = user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca'
                    joined = user.date_joined.strftime('%d/%m/%Y')
                    self.stdout.write(f'   🕐 Último acceso: {last_login}')
                    self.stdout.write(f'   📅 Registrado: {joined}')
                
                self.stdout.write('')
        else:
            self.stdout.write('\n👥 No hay usuarios en esta organización.')

    def show_unassigned_users(self, detailed=False):
        """Mostrar usuarios sin organización"""
        users = User.objects.filter(organization__isnull=True)
        
        self.stdout.write(self.style.WARNING('👤 USUARIOS SIN ORGANIZACIÓN'))
        self.stdout.write('=' * 40)
        
        if not users:
            self.stdout.write('✅ Todos los usuarios están asignados a organizaciones.')
            return
        
        self.stdout.write(f'Total: {users.count()} usuarios\n')
        
        for user in users:
            status_icon = "✅" if user.is_active else "❌"
            role_icon = "⭐" if user.is_superuser else "👤"
            role_text = "Superusuario" if user.is_superuser else "Usuario"
            
            self.stdout.write(f'{status_icon} {role_icon} {user.username}')
            self.stdout.write(f'   📧 Email: {user.email}')
            self.stdout.write(f'   🎭 Rol: {role_text}')
            
            if detailed:
                last_login = user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca'
                joined = user.date_joined.strftime('%d/%m/%Y')
                self.stdout.write(f'   🕐 Último acceso: {last_login}')
                self.stdout.write(f'   📅 Registrado: {joined}')
            
            self.stdout.write('') 