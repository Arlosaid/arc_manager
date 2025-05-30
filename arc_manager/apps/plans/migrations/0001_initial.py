# Generated by Django 5.2 on 2025-05-28 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('gratuito', 'Gratuito'), ('basico', 'Básico')], max_length=50, unique=True, verbose_name='Nombre del plan')),
                ('display_name', models.CharField(max_length=100, verbose_name='Nombre para mostrar')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('max_users', models.PositiveIntegerField(verbose_name='Máximo de usuarios')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Precio mensual')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
            ],
            options={
                'verbose_name': 'Plan',
                'verbose_name_plural': 'Planes',
                'ordering': ['price', 'max_users'],
            },
        ),
    ]
