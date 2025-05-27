from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from orgs.models import Organization

class Command(BaseCommand):
    help = 'Crear una nueva organización'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Nombre de la organización')
        parser.add_argument(
            '--slug',
            type=str,
            help='Slug personalizado (se genera automáticamente si no se proporciona)'
        )
        parser.add_argument(
            '--description',
            type=str,
            help='Descripción de la organización'
        )
        parser.add_argument(
            '--max-users',
            type=int,
            default=10,
            help='Número máximo de usuarios (por defecto: 10)'
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Crear la organización como inactiva'
        )

    def handle(self, *args, **options):
        name = options['name']
        slug = options['slug'] or slugify(name)
        description = options['description'] or ''
        max_users = options['max_users']
        is_active = not options['inactive']

        # Verificar si ya existe una organización con ese slug
        if Organization.objects.filter(slug=slug).exists():
            raise CommandError(f'Ya existe una organización con el slug "{slug}"')

        try:
            organization = Organization.objects.create(
                name=name,
                slug=slug,
                description=description,
                max_users=max_users,
                is_active=is_active
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Organización "{organization.name}" creada exitosamente con ID {organization.id}'
                )
            )
            self.stdout.write(f'Slug: {organization.slug}')
            self.stdout.write(f'Máximo de usuarios: {organization.max_users}')
            self.stdout.write(f'Estado: {"Activa" if organization.is_active else "Inactiva"}')
            
        except Exception as e:
            raise CommandError(f'Error al crear la organización: {str(e)}') 