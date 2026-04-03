#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cha.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Administrator

def check_and_create_admin():
    try:
        user = User.objects.get(username='ADM1')
        admin_profile = getattr(user, 'admin_profile', None)
        if admin_profile:
            print('ADM1 has admin profile - OK')
        else:
            Administrator.objects.create(user=user, level='Senior')
            print('Created admin profile for ADM1')
    except User.DoesNotExist:
        user = User.objects.create_user(username='ADM1', password='ADM', first_name='Administrator', last_name='One')
        Administrator.objects.create(user=user, level='Senior')
        print('Created ADM1 user and admin profile')

if __name__ == '__main__':
    check_and_create_admin()