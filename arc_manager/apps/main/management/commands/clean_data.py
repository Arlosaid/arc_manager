# arc_manager/apps/main/management/commands/clean_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.orgs.models import Organization
from apps.plans.models import Subscription, UpgradeRequest, Payment
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes all organizations, subscriptions, and non-superuser users.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting data cleanup...'))

        # Delete related objects first
        self.stdout.write('Deleting upgrade requests...')
        requests_deleted, _ = UpgradeRequest.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {requests_deleted} upgrade requests.'))
        
        self.stdout.write('Deleting payments...')
        payments_deleted, _ = Payment.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {payments_deleted} payments.'))

        self.stdout.write('Deleting subscriptions...')
        subscriptions_deleted, _ = Subscription.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {subscriptions_deleted} subscriptions.'))
        
        self.stdout.write('Deleting organizations...')
        orgs_deleted, _ = Organization.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {orgs_deleted} organizations.'))

        self.stdout.write('Deleting non-superuser users...')
        non_superusers = User.objects.filter(is_superuser=False)
        users_deleted, _ = non_superusers.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {users_deleted} non-superuser users.'))
        
        superusers_count = User.objects.filter(is_superuser=True).count()
        self.stdout.write(self.style.NOTICE(f'{superusers_count} superuser(s) remain.'))

        self.stdout.write(self.style.SUCCESS('Data cleanup complete.')) 