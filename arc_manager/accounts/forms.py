from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Por favor, introduce un correo electrónico y contraseña válidos. '
                         'Ten en cuenta que ambos campos pueden ser sensibles a mayúsculas y minúsculas.',
        'inactive': 'Esta cuenta está inactiva.',
    }
    
    def clean(self):
        try:
            return super().clean()
        except ValidationError as e:
            # Si ocurre un error, asegúrate de que use los mensajes en español
            if hasattr(e, 'message') and e.message == 'Please enter a correct username and password. Note that both fields may be case-sensitive.':
                e.message = self.error_messages['invalid_login']
            raise e