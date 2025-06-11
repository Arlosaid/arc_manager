# Generated manually to populate empty names before making them required

from django.db import migrations


def populate_empty_names(apps, schema_editor):
    """Poblar nombres vacíos con datos del email"""
    User = apps.get_model('accounts', 'User')
    
    users_to_update = User.objects.filter(
        first_name__in=['', None]
    ) | User.objects.filter(
        last_name__in=['', None]
    )
    
    for user in users_to_update:
        if not user.first_name or not user.last_name:
            # Usar el email para generar nombres
            email_part = user.email.split('@')[0] if user.email else 'Usuario'
            
            if '.' in email_part:
                parts = email_part.split('.')
                if len(parts) >= 2:
                    user.first_name = parts[0].capitalize() if not user.first_name else user.first_name
                    user.last_name = parts[1].capitalize() if not user.last_name else user.last_name
                else:
                    user.first_name = email_part.capitalize() if not user.first_name else user.first_name
                    user.last_name = 'Usuario' if not user.last_name else user.last_name
            else:
                user.first_name = email_part.capitalize() if not user.first_name else user.first_name
                user.last_name = 'Usuario' if not user.last_name else user.last_name
            
            user.save()


def reverse_populate_names(apps, schema_editor):
    """No hay operación reversa, los nombres se quedan como están"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_display_name'),
    ]

    operations = [
        migrations.RunPython(populate_empty_names, reverse_populate_names),
    ] 