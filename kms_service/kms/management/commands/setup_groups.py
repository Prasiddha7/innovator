from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create user groups for role-based access control'

    def handle(self, *args, **options):
        # Define role groups
        roles = ['teacher', 'admin', 'coordinator', 'principal']
        
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created group "{role}"')
                )
            else:
                self.stdout.write(f'Group "{role}" already exists')
        
        self.stdout.write(self.style.SUCCESS('All groups created successfully'))
