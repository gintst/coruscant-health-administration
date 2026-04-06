"""
URL configuration for cha project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.static import serve

from core import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('emergency/add-patient/', views.emergency_add_patient, name='emergency_add_patient'),
    path('admin/monitoring/', views.admin_monitoring, name='admin_monitoring'),
    path('admin/register-user/', views.admin_register_user, name='admin_register_user'),
    path('admin/approve-user/', views.approve_user, name='approve_user'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reading/add/', views.add_reading, name='add_reading'),
    path('patient/<int:patient_id>/record/', views.patient_record, name='patient_record'),
    path('patient/<int:patient_id>/report/', views.doctor_report, name='doctor_report'),
    path('patient/<int:patient_id>/order/', views.submit_order, name='submit_order'),
    path('order/<int:order_id>/process/', views.process_order, name='process_order'),
    path('document/upload/', views.upload_document, name='upload_document'),
    path('document/<int:document_id>/download/', views.download_document, name='download_document'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += [
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.BASE_DIR / "core" / "static"}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
