from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (Administrator, Department, Doctor, DoctorReport,
                     EmergencyService, HealthReading, Order, Patient, Document)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "date_of_birth")
    list_filter = ("location", "date_of_birth")
    search_fields = ("user__username", "user__first_name", "user__last_name", "location")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty", "is_active")
    list_filter = ("specialty", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name", "specialty")


@admin.register(EmergencyService)
class EmergencyServiceAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name", "role")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("user", "department_name", "is_active")
    list_filter = ("department_name", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name", "department_name")


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ("user", "level", "is_active")
    list_filter = ("level", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name", "level")


@admin.register(HealthReading)
class HealthReadingAdmin(admin.ModelAdmin):
    list_display = ("patient", "recorded_at", "heart_rate", "blood_pressure", "oxygen_saturation")
    list_filter = ("recorded_at", "patient")
    search_fields = ("patient__user__username", "note")
    date_hierarchy = "recorded_at"


@admin.register(DoctorReport)
class DoctorReportAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "created_at")
    list_filter = ("created_at", "doctor")
    search_fields = ("patient__user__username", "doctor__user__username", "report_text")
    date_hierarchy = "created_at"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "created_at", "status", "result")
    list_filter = ("created_at", "status", "doctor")
    search_fields = ("patient__user__username", "doctor__user__username", "description")
    date_hierarchy = "created_at"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("uploaded_by", "uploaded_at", "encrypted")
    list_filter = ("uploaded_at", "encrypted")
    search_fields = ("uploaded_by__username", "file")
    date_hierarchy = "uploaded_at"


# Customize User admin to show related profiles
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('get_groups', 'get_user_type')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

    def get_user_type(self, obj):
        if hasattr(obj, 'patient_profile'):
            return 'Patient'
        elif hasattr(obj, 'doctor_profile'):
            return 'Doctor'
        elif hasattr(obj, 'emergency_profile'):
            return 'Emergency'
        elif hasattr(obj, 'department_profile'):
            return 'Department'
        elif hasattr(obj, 'admin_profile'):
            return 'Administrator'
        return 'Unknown'
    get_user_type.short_description = 'User Type'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
