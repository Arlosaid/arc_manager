from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.orgs.models import Organization
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear datos de ejemplo: organizaciones y usuarios para desarrollo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Eliminar todos los datos existentes antes de crear nuevos'
        )
        parser.add_argument(
            '--orgs',
            type=int,
            default=3,
            help='Número de organizaciones a crear (por defecto: 3)'
        )
        parser.add_argument(
            '--users-per-org',
            type=int,
            default=5,
            help='Número de usuarios por organización (por defecto: 5)'
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            # No eliminar superusuarios
            User.objects.filter(is_superuser=False).delete()
            Organization.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Datos eliminados.'))

        num_orgs = options['orgs']
        users_per_org = options['users_per_org']

        # Datos de ejemplo para organizaciones
        org_data = [
            {
                'name': 'TechCorp Solutions',
                'description': 'Empresa de desarrollo de software y consultoría tecnológica',
                'max_users': 20
            },
            {
                'name': 'Marketing Digital Pro',
                'description': 'Agencia especializada en marketing digital y redes sociales',
                'max_users': 15
            },
            {
                'name': 'Consultores Financieros',
                'description': 'Servicios de consultoría financiera y contable',
                'max_users': 10
            },
            {
                'name': 'Diseño Creativo Studio',
                'description': 'Estudio de diseño gráfico y desarrollo web',
                'max_users': 12
            },
            {
                'name': 'Educación Online',
                'description': 'Plataforma de cursos y educación en línea',
                'max_users': 25
            }
        ]

        # Nombres de ejemplo para usuarios
        nombres = [
            'Ana García', 'Carlos López', 'María Rodríguez', 'Juan Martínez',
            'Laura Sánchez', 'Pedro González', 'Carmen Fernández', 'Miguel Torres',
            'Isabel Ruiz', 'Francisco Moreno', 'Pilar Jiménez', 'Antonio Álvarez',
            'Rosa Romero', 'Manuel Navarro', 'Cristina Muñoz', 'José Iglesias',
            'Elena Medina', 'David Garrido', 'Lucía Serrano', 'Alejandro Peña'
        ]

        self.stdout.write(f'Creando {num_orgs} organizaciones...')
        
        created_orgs = []
        for i in range(num_orgs):
            if i < len(org_data):
                data = org_data[i]
            else:
                data = {
                    'name': f'Organización {i+1}',
                    'description': f'Descripción de la organización {i+1}',
                    'max_users': random.randint(10, 30)
                }
            
            org, created = Organization.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'is_active': True
                }
            )
            
            created_orgs.append(org)
            
            if created:
                status = "CREADA"
            else:
                status = "YA EXISTÍA"
            
            self.stdout.write(f'  ✓ {org.name} (ID: {org.id}) - {status}')

        self.stdout.write(f'\nCreando usuarios para cada organización...')
        
        total_users_created = 0
        for org in created_orgs:
            self.stdout.write(f'\n  Organización: {org.name}')
            
            # Crear usuarios para esta organización
            org_users_created = 0
            for i in range(min(users_per_org, org.get_max_users())):
                if i < len(nombres):
                    nombre_completo = nombres[i]
                else:
                    nombre_completo = f'Usuario {i+1}'
                
                # Generar email único
                nombre_parts = nombre_completo.lower().split()
                base_email = f"{nombre_parts[0]}.{nombre_parts[-1]}@{org.id}.demo"
                email = base_email
                counter = 1
                while User.objects.filter(email=email).exists():
                    email = f"{nombre_parts[0]}.{nombre_parts[-1]}{counter}@{org.id}.demo"
                    counter += 1

                # Determinar si será admin (primer usuario de cada org)
                is_admin = (i == 0)
                
                user, created = User.objects.get_or_create(
                    username=f'{nombre_parts[0].lower()}_{nombre_parts[-1].lower()}_org{org.id}',
                    defaults={
                        'email': email,
                        'first_name': nombre_parts[0],
                        'last_name': nombre_parts[-1],
                        'is_active': True,
                        'is_org_admin': is_admin,
                        'organization': org
                    }
                )
                
                if created:
                    user.set_password('demo123')
                    user.save()
                
                role = "Admin" if is_admin else "Usuario"
                self.stdout.write(f'    ✓ {user.username} ({user.email}) - {role}')
                org_users_created += 1
                total_users_created += 1

            self.stdout.write(f'    Total usuarios en {org.name}: {org_users_created}')

        # Resumen final
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Datos de ejemplo creados exitosamente!'))
        self.stdout.write(f'📊 Resumen:')
        self.stdout.write(f'   • Organizaciones: {len(created_orgs)}')
        self.stdout.write(f'   • Usuarios totales: {total_users_created}')
        
        self.stdout.write(f'\n📝 Credenciales de acceso:')
        self.stdout.write(f'   • Contraseña para todos los usuarios: demo123')
        self.stdout.write(f'   • Los primeros usuarios de cada organización son administradores')
        
        self.stdout.write(f'\n🔗 URLs útiles:')
        self.stdout.write(f'   • Lista de organizaciones: /organizaciones/')
        self.stdout.write(f'   • Mi organización: /organizaciones/mi-organizacion/')
        self.stdout.write(f'   • Admin de Django: /admin/')

        # Mostrar algunos usuarios de ejemplo
        self.stdout.write(f'\n👥 Algunos usuarios de ejemplo:')
        for org in created_orgs[:2]:  # Mostrar solo las primeras 2 orgs
            admin_user = org.users.filter(is_org_admin=True).first()
            if admin_user:
                self.stdout.write(f'   • {admin_user.email} (Admin de {org.name})')
            
            regular_user = org.users.filter(is_org_admin=False).first()
            if regular_user:
                self.stdout.write(f'   • {regular_user.email} (Usuario de {org.name})') 