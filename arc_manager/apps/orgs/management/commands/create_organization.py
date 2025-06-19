from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from apps.orgs.models import Organization

class Command(BaseCommand):
    help = 'Crear una nueva organización'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Nombre de la organización')
        parser.add_argument('--description', type=str, help='Descripción de la organización')
        parser.add_argument('--max-users', type=int, default=3, help='Número máximo de usuarios')
        parser.add_argument('--inactive', action='store_true', help='Crear organización inactiva')

    def handle(self, *args, **options):
        name = options['name']
        description = options['description'] or ''
        max_users = options['max_users']
        is_active = not options['inactive']

        try:
            organization = Organization.objects.create(
                name=name,
                description=description,
                is_active=is_active
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Organización "{organization.name}" creada exitosamente con ID {organization.id}'
                )
            )
            self.stdout.write(f'ID: {organization.id}')
            self.stdout.write(f'Estado: {"Activa" if organization.is_active else "Inactiva"}')
            
        except Exception as e:
            raise CommandError(f'Error al crear la organización: {str(e)}') 