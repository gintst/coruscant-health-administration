from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import EmergencyService, Department, Administrator

class Command(BaseCommand):
    help = 'Create default users for different roles'

    def handle(self, *args, **options):
        # Emergency Services - only EME
        if not User.objects.filter(username='EME').exists():
            eme_user = User.objects.create_user(username='EME', password='EME', first_name='Emergency', last_name='Service')
            EmergencyService.objects.create(user=eme_user, role='EME')
            self.stdout.write(self.style.SUCCESS('Created EME user'))

        # Department
        if not User.objects.filter(username='DEP1').exists():
            dep1_user = User.objects.create_user(username='DEP1', password='DEP', first_name='Department', last_name='User1')
            Department.objects.create(user=dep1_user, department_name='General')
            self.stdout.write(self.style.SUCCESS('Created DEP1 user'))

        if not User.objects.filter(username='DEP2').exists():
            dep2_user = User.objects.create_user(username='DEP2', password='DEP', first_name='Department', last_name='User2')
            Department.objects.create(user=dep2_user, department_name='Administration')
            self.stdout.write(self.style.SUCCESS('Created DEP2 user'))

        # Administrator
        if not User.objects.filter(username='ADM1').exists():
            adm1_user = User.objects.create_user(username='ADM1', password='ADM', first_name='Administrator', last_name='One')
            Administrator.objects.create(user=adm1_user, level='Senior')
            self.stdout.write(self.style.SUCCESS('Created ADM1 user'))

        if not User.objects.filter(username='ADM2').exists():
            adm2_user = User.objects.create_user(username='ADM2', password='ADM', first_name='Administrator', last_name='Two')
            Administrator.objects.create(user=adm2_user, level='Junior')
            self.stdout.write(self.style.SUCCESS('Created ADM2 user'))

        self.stdout.write(self.style.SUCCESS('All users created successfully!'))