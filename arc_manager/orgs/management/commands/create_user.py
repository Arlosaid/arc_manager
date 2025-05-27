from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from orgs.models import Organization

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear un nuevo usuario y asignarlo a una organización'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email del usuario')
        parser.add_argument(
            '--name',
            type=str,
            help='Nombre completo del usuario'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='demo123',
            help='Contraseña del usuario (por defecto: demo123)'
        )
        parser.add_argument(
            '--org-slug',
            type=str,
            help='Slug de la organización a la que asignar el usuario'
        )
        parser.add_argument(
            '--org-id',
            type=int,
            help='ID de la organización a la que asignar el usuario'
        )
        parser.add_argument(
            '--admin',
            action='store_true',
            help='Hacer al usuario administrador de la organización'
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Crear como superusuario'
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Crear el usuario como inactivo'
        )

    def handle(self, *args, **options):
        email = options['email']
        name = options['name'] or email.split('@')[0]
        password = options['password']
        is_admin = options['admin']
        is_superuser = options['superuser']
        is_active = not options['inactive']

        # Verificar si el email ya existe
        if User.objects.filter(email=email).exists():
            raise CommandError(f'Ya existe un usuario con el email "{email}"')

        # Buscar organización si se especificó
        organization = None
        if options['org_slug']:
            try:
                organization = Organization.objects.get(slug=options['org_slug'])
            except Organization.DoesNotExist:
                raise CommandError(f'No existe una organización con slug "{options["org_slug"]}"')
        elif options['org_id']:
            try:
                organization = Organization.objects.get(id=options['org_id'])
            except Organization.DoesNotExist:
                raise CommandError(f'No existe una organización con ID "{options["org_id"]}"')

        # Verificar límites de la organización
        if organization and not organization.can_add_user() and not is_superuser:
            raise CommandError(
                f'La organización "{organization.name}" ha alcanzado su límite de '
                f'{organization.max_users} usuarios'
            )

        try:
            if is_superuser:
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    username=name,
                    organization=organization
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Superusuario "{user.username}" creado exitosamente')
                )
            else:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    username=name,
                    organization=organization,
                    is_org_admin=is_admin,
                    is_active=is_active
                )
                role = "Administrador" if is_admin else "Usuario"
                status = "Activo" if is_active else "Inactivo"
                self.stdout.write(
                    self.style.SUCCESS(f'{role} "{user.username}" creado exitosamente ({status})')
                )

            # Mostrar información del usuario creado
            self.stdout.write(f'📧 Email: {user.email}')
            self.stdout.write(f'👤 Nombre: {user.username}')
            self.stdout.write(f'🔑 Contraseña: {password}')
            
            if organization:
                self.stdout.write(f'🏢 Organización: {organization.name}')
                self.stdout.write(f'👥 Usuarios en la organización: {organization.get_user_count()}/{organization.max_users}')
            else:
                self.stdout.write(f'🏢 Organización: Sin asignar')

            if is_superuser:
                self.stdout.write(f'⭐ Tipo: Superusuario')
            elif is_admin:
                self.stdout.write(f'👑 Tipo: Administrador de organización')
            else:
                self.stdout.write(f'👤 Tipo: Usuario regular')

        except Exception as e:
            raise CommandError(f'Error al crear el usuario: {str(e)}') 