#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cha.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import EmergencyService, Department, Administrator

def create_users():
    # Emergency Services
    ema_user = User.objects.create_user(username='EMA', password='EMA', first_name='Emergency', last_name='Assistant')
    EmergencyService.objects.create(user=ema_user, role='EMA')

    eme_user = User.objects.create_user(username='EME', password='EME', first_name='Emergency', last_name='Expert')
    EmergencyService.objects.create(user=eme_user, role='EME')

    # Department
    dep1_user = User.objects.create_user(username='DEP1', password='DEP', first_name='Department', last_name='User1')
    Department.objects.create(user=dep1_user, department_name='General')

    dep2_user = User.objects.create_user(username='DEP2', password='DEP', first_name='Department', last_name='User2')
    Department.objects.create(user=dep2_user, department_name='Administration')

    # Administrator
    adm1_user = User.objects.create_user(username='ADM1', password='ADM', first_name='Administrator', last_name='One')
    Administrator.objects.create(user=adm1_user, level='Senior')

    adm2_user = User.objects.create_user(username='ADM2', password='ADM', first_name='Administrator', last_name='Two')
    Administrator.objects.create(user=adm2_user, level='Junior')

    print('All users created successfully!')

if __name__ == '__main__':
    create_users()