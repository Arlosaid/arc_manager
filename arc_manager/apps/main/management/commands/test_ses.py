from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Prueba el envío de emails con Amazon SES'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email de destino para la prueba'
        )

    def handle(self, *args, **options):
        email_destino = options['email']
        
        try:
            # Enviar email de prueba
            send_mail(
                subject='Prueba de Amazon SES - ARC Manager',
                message='Este es un email de prueba desde ARC Manager usando Amazon SES.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_destino],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email enviado exitosamente a {email_destino}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al enviar email: {str(e)}')
            ) 