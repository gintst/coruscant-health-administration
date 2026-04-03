from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone


def document_cipher():
    return Fernet(settings.DOCUMENT_ENCRYPTION_KEY)

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    specialty = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Doctor: {self.user.get_full_name() or self.user.username} ({self.specialty})"


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="orders")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="orders")
    description = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    result = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_completed(self, result=""):
        self.status = self.STATUS_COMPLETED
        self.result = result
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.patient} ({self.status})"


class HealthReading(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="health_readings")
    recorded_at = models.DateTimeField(auto_now_add=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=32, blank=True)
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Reading for {self.patient} at {self.recorded_at.isoformat()}"


class DoctorReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="doctor_reports")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor_reports")
    report_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.patient} by {self.doctor}"


class EmergencyService(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="emergency_profile")
    role = models.CharField(max_length=255, blank=True)  # e.g., EMA, EME
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Emergency Service: {self.user.get_full_name() or self.user.username} ({self.role})"


class Department(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="department_profile")
    department_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Department: {self.user.get_full_name() or self.user.username} ({self.department_name})"


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    level = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Administrator: {self.user.get_full_name() or self.user.username} ({self.level})"


class Document(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="documents/")
    original_name = models.CharField(max_length=255, blank=True)
    encrypted = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.file and not self.encrypted:
            plaintext = self.file.read()
            encrypted_payload = document_cipher().encrypt(plaintext)
            self.original_name = self.original_name or self.file.name.split("/")[-1]
            self.file.save(
                f"{self.original_name}.encrypted",
                ContentFile(encrypted_payload),
                save=False,
            )
            self.encrypted = True
        super().save(*args, **kwargs)

    def get_download_content(self):
        if not self.file:
            return None
        with self.file.open('rb') as f:
            data = f.read()
        if not self.encrypted:
            return data
        return document_cipher().decrypt(data)

    def __str__(self):
        return f"Document {self.id} by {self.uploaded_by.username}"
