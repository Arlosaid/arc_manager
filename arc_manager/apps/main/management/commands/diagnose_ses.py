from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError


class Command(BaseCommand):
    help = 'Diagnóstico completo de la configuración de Amazon SES'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-email',
            type=str,
            help='Email para enviar prueba (opcional)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('🔍 DIAGNÓSTICO COMPLETO DE SES'))
        self.stdout.write('=' * 60)
        
        # 1. Verificar variables de entorno
        self.check_environment_variables()
        
        # 2. Verificar configuración de Django
        self.check_django_config()
        
        # 3. Verificar conexión con AWS SES
        self.check_ses_connection()
        
        # 4. Verificar dominios/emails verificados
        self.check_verified_identities()
        
        # 5. Verificar cuotas y límites
        self.check_ses_limits()
        
        # 6. Enviar email de prueba si se proporciona
        test_email = options.get('test_email')
        if test_email:
            self.test_email_sending(test_email)
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Diagnóstico completado'))

    def check_environment_variables(self):
        self.stdout.write('\n📋 1. Verificando variables de entorno...')
        
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_SES_REGION',
            'DEFAULT_FROM_EMAIL'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                # Mostrar solo los primeros 4 caracteres por seguridad
                display_value = value[:4] + '***' if len(value) > 4 else '***'
                self.stdout.write(f'   ✅ {var}: {display_value}')
            else:
                missing_vars.append(var)
                self.stdout.write(f'   ❌ {var}: NO CONFIGURADO')
        
        if missing_vars:
            self.stdout.write(self.style.ERROR(f'   ⚠️  Variables faltantes: {", ".join(missing_vars)}'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✅ Todas las variables están configuradas'))

    def check_django_config(self):
        self.stdout.write('\n⚙️  2. Verificando configuración de Django...')
        
        # Verificar EMAIL_BACKEND
        email_backend = getattr(settings, 'EMAIL_BACKEND', 'No configurado')
        self.stdout.write(f'   📧 EMAIL_BACKEND: {email_backend}')
        
        if 'django_ses' in email_backend:
            self.stdout.write(self.style.SUCCESS('   ✅ SES Backend configurado correctamente'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠️  SES Backend no configurado'))
        
        # Verificar DEFAULT_FROM_EMAIL
        default_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'No configurado')
        self.stdout.write(f'   📧 DEFAULT_FROM_EMAIL: {default_email}')
        
        # Verificar modo DEBUG
        debug_mode = getattr(settings, 'DEBUG', False)
        self.stdout.write(f'   🐞 DEBUG: {debug_mode}')
        
        # Verificar detección de AWS
        is_aws = os.environ.get('AWS_EXECUTION_ENV') is not None
        self.stdout.write(f'   ☁️  Ambiente AWS detectado: {is_aws}')

    def check_ses_connection(self):
        self.stdout.write('\n🔗 3. Verificando conexión con Amazon SES...')
        
        try:
            # Intentar conectar con SES
            ses_client = boto3.client(
                'ses',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_SES_REGION', 'us-east-1')
            )
            
            # Hacer una llamada simple para verificar credenciales
            ses_client.get_send_quota()
            self.stdout.write(self.style.SUCCESS('   ✅ Conexión con SES exitosa'))
            return ses_client
            
        except NoCredentialsError:
            self.stdout.write(self.style.ERROR('   ❌ Credenciales AWS no encontradas'))
            return None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self.stdout.write(self.style.ERROR(f'   ❌ Error de credenciales: {error_code}'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error de conexión: {str(e)}'))
            return None

    def check_verified_identities(self):
        self.stdout.write('\n📧 4. Verificando identidades verificadas...')
        
        try:
            ses_client = boto3.client(
                'ses',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_SES_REGION', 'us-east-1')
            )
            
            # Obtener emails verificados
            response = ses_client.list_verified_email_addresses()
            verified_emails = response.get('VerifiedEmailAddresses', [])
            
            # Obtener dominios verificados
            domains_response = ses_client.list_identities(IdentityType='Domain')
            verified_domains = domains_response.get('Identities', [])
            
            if verified_emails:
                self.stdout.write('   📧 Emails verificados:')
                for email in verified_emails:
                    self.stdout.write(f'      • {email}')
            else:
                self.stdout.write('   ⚠️  No hay emails verificados')
            
            if verified_domains:
                self.stdout.write('   🌐 Dominios verificados:')
                for domain in verified_domains:
                    self.stdout.write(f'      • {domain}')
            else:
                self.stdout.write('   ⚠️  No hay dominios verificados')
            
            # Verificar si DEFAULT_FROM_EMAIL está verificado
            default_email = os.environ.get('DEFAULT_FROM_EMAIL', '')
            if default_email:
                email_verified = default_email in verified_emails
                domain_verified = any(default_email.split('@')[1] == domain for domain in verified_domains) if '@' in default_email else False
                
                if email_verified or domain_verified:
                    self.stdout.write(self.style.SUCCESS(f'   ✅ DEFAULT_FROM_EMAIL está verificado'))
                else:
                    self.stdout.write(self.style.ERROR(f'   ❌ DEFAULT_FROM_EMAIL no está verificado: {default_email}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error verificando identidades: {str(e)}'))

    def check_ses_limits(self):
        self.stdout.write('\n📊 5. Verificando cuotas y límites de SES...')
        
        try:
            ses_client = boto3.client(
                'ses',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_SES_REGION', 'us-east-1')
            )
            
            # Obtener cuotas
            quota_response = ses_client.get_send_quota()
            sent_last_24h = quota_response.get('SentLast24Hours', 0)
            max_24h = quota_response.get('Max24HourSend', 0)
            max_per_second = quota_response.get('MaxSendRate', 0)
            
            self.stdout.write(f'   📈 Emails enviados (últimas 24h): {sent_last_24h}/{max_24h}')
            self.stdout.write(f'   ⚡ Velocidad máxima: {max_per_second} emails/segundo')
            
            # Verificar si estamos en sandbox
            if max_24h == 200:  # Límite típico del sandbox
                self.stdout.write(self.style.WARNING('   ⚠️  Posiblemente en modo SANDBOX (límite 200 emails/día)'))
                self.stdout.write('       Para producción, solicita salir del sandbox en AWS Console')
            else:
                self.stdout.write(self.style.SUCCESS('   ✅ Fuera del modo sandbox'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error verificando límites: {str(e)}'))

    def test_email_sending(self, test_email):
        self.stdout.write(f'\n📬 6. Enviando email de prueba a {test_email}...')
        
        try:
            send_mail(
                subject='🧪 Prueba SES - Diagnóstico ARC Manager',
                message=f'''¡Hola!

Este email fue enviado desde el comando de diagnóstico de ARC Manager.

✅ La configuración de Amazon SES está funcionando correctamente.

Detalles del envío:
- Backend: {getattr(settings, 'EMAIL_BACKEND', 'No configurado')}
- Región: {os.environ.get('AWS_SES_REGION', 'us-east-1')}
- Email origen: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'No configurado')}
- Ambiente AWS: {os.environ.get('AWS_EXECUTION_ENV') is not None}

--
ARC Manager - Diagnóstico SES''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ Email enviado exitosamente a {test_email}'))
            self.stdout.write('   💡 Revisa tu bandeja de entrada (puede tardar unos minutos)')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error enviando email: {str(e)}'))
            
            # Sugerencias basadas en el error
            error_str = str(e).lower()
            if 'not verified' in error_str or 'email address not verified' in error_str:
                self.stdout.write('   💡 Sugerencia: Verifica el email en AWS SES Console')
            elif 'quota' in error_str:
                self.stdout.write('   💡 Sugerencia: Has alcanzado el límite de envío diario')
            elif 'credentials' in error_str:
                self.stdout.write('   💡 Sugerencia: Verifica las credenciales AWS') 