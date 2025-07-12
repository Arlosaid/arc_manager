from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError
import os


class Command(BaseCommand):
    help = 'Configura la base de datos automáticamente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la ejecución incluso si hay errores',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write("🔄 Iniciando configuración de base de datos...")
        
        # Verificar conexión a la base de datos
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('✅ Conexión a base de datos exitosa'))
        except OperationalError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error de conexión a base de datos: {e}')
            )
            if not force:
                return
        
        try:
            # Ejecutar migraciones
            self.stdout.write("🔄 Ejecutando migraciones...")
            call_command('migrate', verbosity=2, interactive=False)
            self.stdout.write(self.style.SUCCESS("✅ Migraciones completadas"))
            
            # Crear superusuario
            self.stdout.write("👤 Configurando superusuario...")
            User = get_user_model()
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    email='admin@example.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='System'
                )
                self.stdout.write(self.style.SUCCESS("✅ Superusuario creado"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Superusuario ya existe"))
            
            # Configurar planes
            self.stdout.write("📋 Configurando planes...")
            try:
                call_command('setup_mvp_plans')
                self.stdout.write(self.style.SUCCESS("✅ Planes configurados"))
            except Exception as e:
                if force:
                    self.stdout.write(self.style.WARNING(f"⚠️ Error en planes: {e}"))
                else:
                    raise
            
            # Recopilar archivos estáticos
            self.stdout.write("📦 Recopilando archivos estáticos...")
            call_command('collectstatic', verbosity=1, interactive=False)
            self.stdout.write(self.style.SUCCESS("✅ Archivos estáticos listos"))
            
            self.stdout.write(self.style.SUCCESS("🎉 ¡Configuración de base de datos completada exitosamente!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error durante la configuración: {e}"))
            if force:
                self.stdout.write(self.style.WARNING("⚠️ Continuando debido a --force"))
            else:
                raise 