from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Prueba la configuración de correos con Amazon SES'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email destino para la prueba (debe estar verificado en SES)',
            required=True
        )

    def handle(self, *args, **options):
        email_destino = options['email']
        
        self.stdout.write(self.style.HTTP_INFO('🔍 Verificando configuración de Amazon SES...'))
        
        # Verificar configuración
        if not hasattr(settings, 'AWS_ACCESS_KEY_ID') or not settings.AWS_ACCESS_KEY_ID:
            self.stdout.write(self.style.ERROR('❌ AWS_ACCESS_KEY_ID no configurado'))
            return
            
        if not hasattr(settings, 'AWS_SECRET_ACCESS_KEY') or not settings.AWS_SECRET_ACCESS_KEY:
            self.stdout.write(self.style.ERROR('❌ AWS_SECRET_ACCESS_KEY no configurado'))
            return
        
        # Verificar credenciales de AWS
        try:
            ses_client = boto3.client(
                'ses',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, 'AWS_SES_REGION_NAME', 'us-east-1')
            )
            
            # Verificar identidades verificadas
            response = ses_client.list_verified_email_addresses()
            verified_emails = response.get('VerifiedEmailAddresses', [])
            
            self.stdout.write(self.style.SUCCESS('✅ Conexión con SES establecida'))
            self.stdout.write(f'📧 Emails verificados: {", ".join(verified_emails)}')
            
            # Verificar cuotas
            quota_response = ses_client.get_send_quota()
            sent_last_24h = quota_response.get('SentLast24Hours', 0)
            max_24h = quota_response.get('Max24HourSend', 0)
            max_per_second = quota_response.get('MaxSendRate', 0)
            
            self.stdout.write(f'📊 Cuota SES: {sent_last_24h}/{max_24h} emails (últimas 24h)')
            self.stdout.write(f'⚡ Velocidad máxima: {max_per_second} emails/segundo')
            
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'❌ Error de credenciales AWS: {e}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error de configuración: {e}'))
            return
        
        # Enviar email de prueba
        try:
            self.stdout.write(self.style.HTTP_INFO(f'📬 Enviando email de prueba a {email_destino}...'))
            
            send_mail(
                subject='🧪 Prueba de configuración ARC Manager',
                message='''
¡Hola!

Este es un email de prueba para verificar que la configuración de Amazon SES está funcionando correctamente.

✅ La configuración de correos está operativa.

--
ARC Manager
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_destino],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Email enviado exitosamente a {email_destino}'))
            self.stdout.write('💡 Revisa tu bandeja de entrada (puede tardar unos minutos)')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error enviando email: {e}'))
            self.stdout.write('💡 Verifica que el email destino esté verificado en SES') 