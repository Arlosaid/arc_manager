# Generated manually on 2025-01-24 to simplify UpgradeRequest model

from django.db import migrations, models


class Migration(migrations.Migration):
    
    dependencies = [
        ('plans', '0003_upgraderequest'),
    ]
    
    operations = [
        # Remover campos que ya no se usan
        migrations.RemoveField(
            model_name='upgraderequest',
            name='payment_reference',
        ),
        migrations.RemoveField(
            model_name='upgraderequest',
            name='payment_proof_info',
        ),
        migrations.RemoveField(
            model_name='upgraderequest',
            name='completed_date',
        ),
        # Actualizar choices del campo status
        migrations.AlterField(
            model_name='upgraderequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pendiente de Aprobación'), 
                    ('approved', 'Aprobada'), 
                    ('rejected', 'Rechazada'), 
                    ('cancelled', 'Cancelada')
                ], 
                default='pending', 
                max_length=20, 
                verbose_name='Estado'
            ),
        ),
        # Agregar default al payment_method
        migrations.AlterField(
            model_name='upgraderequest',
            name='payment_method',
            field=models.CharField(
                blank=True, 
                default='transferencia', 
                max_length=50, 
                verbose_name='Método de Pago Preferido'
            ),
        ),
    ] 