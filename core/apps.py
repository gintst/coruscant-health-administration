from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        post_migrate.connect(create_default_users, sender=self)

        # Workaround for Django 4.2 + Python 3.14 BaseContext.__copy__ bug
        try:
            from django.template.context import BaseContext
            from django.utils.functional import keep_lazy_text

            original_copy = BaseContext.__copy__

            def safe_copy(self):
                try:
                    return original_copy(self)
                except AttributeError as e:
                    if "'super' object has no attribute 'dicts'" in str(e):
                        duplicate = self.__class__.__new__(self.__class__)
                        # copy attributes while preserving context dicts
                        if hasattr(self, '__dict__'):
                            for k, v in self.__dict__.items():
                                if k == 'dicts':
                                    continue
                                setattr(duplicate, k, v)
                        duplicate.dicts = list(self.dicts)
                        return duplicate
                    raise

            BaseContext.__copy__ = safe_copy
        except Exception:
            pass


@receiver(post_migrate)
def create_default_users(sender, **kwargs):
    if sender.name == 'core':
        from django.contrib.auth.models import User
        from .models import EmergencyService, Department, Administrator

        # Emergency Services - only EME
        if not User.objects.filter(username='EME').exists():
            eme_user = User.objects.create_user(username='EME', password='EME', first_name='Emergency', last_name='Service')
            EmergencyService.objects.create(user=eme_user, role='EME')

        # Department
        if not User.objects.filter(username='DEP1').exists():
            dep1_user = User.objects.create_user(username='DEP1', password='DEP', first_name='Department', last_name='User1')
            Department.objects.create(user=dep1_user, department_name='General')

        if not User.objects.filter(username='DEP2').exists():
            dep2_user = User.objects.create_user(username='DEP2', password='DEP', first_name='Department', last_name='User2')
            Department.objects.create(user=dep2_user, department_name='Administration')

        # Administrator
        if not User.objects.filter(username='ADM1').exists():
            adm1_user = User.objects.create_user(username='ADM1', password='ADM', first_name='Administrator', last_name='One')
            adm1_user.is_staff = True
            adm1_user.is_superuser = True
            adm1_user.save()
            Administrator.objects.create(user=adm1_user, level='Senior')

        if not User.objects.filter(username='ADM2').exists():
            adm2_user = User.objects.create_user(username='ADM2', password='ADM', first_name='Administrator', last_name='Two')
            adm2_user.is_staff = True
            adm2_user.is_superuser = True
            adm2_user.save()
            Administrator.objects.create(user=adm2_user, level='Junior')
