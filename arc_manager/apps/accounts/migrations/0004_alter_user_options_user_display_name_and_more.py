# Generated by Django 5.2 on 2025-06-10 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_organization'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('orgs', '0007_remove_organization_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddField(
            model_name='user',
            name='display_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Nombre para mostrar'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(condition=models.Q(('is_superuser', True), ('organization__isnull', False), ('is_active', False), _connector='OR'), name='users_must_have_org_or_be_superuser_or_inactive'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(fields=('email',), name='unique_email'),
        ),
    ]
