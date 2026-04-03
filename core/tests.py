from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Administrator, Department, Doctor, Document, EmergencyService, HealthReading, Order, Patient


@override_settings(MEDIA_ROOT="/tmp/heal-test-media")
class CoreModelTests(TestCase):
    def test_create_patient_and_doctor(self):
        user_p = User.objects.create_user(username="testpatient", password="password")
        patient = Patient.objects.create(
            user=user_p,
            location="Coruscant",
            date_of_birth="2000-01-01",
            is_approved=True,
        )
        self.assertEqual(patient.user.username, "testpatient")

        user_d = User.objects.create_user(username="testdoctor", password="password")
        doctor = Doctor.objects.create(user=user_d, specialty="General", is_approved=True)
        self.assertEqual(doctor.specialty, "General")

    def test_order_and_state_transition(self):
        user_p = User.objects.create_user(username="opatient", password="password")
        patient = Patient.objects.create(user=user_p, location="Coruscant", is_approved=True)
        user_d = User.objects.create_user(username="odoctor", password="password")
        doctor = Doctor.objects.create(user=user_d, specialty="Cardio", is_approved=True)
        order = Order.objects.create(patient=patient, doctor=doctor, description="CT scan")

        self.assertEqual(order.status, Order.STATUS_PENDING)
        order.mark_completed(result="CT normal")
        self.assertEqual(order.status, Order.STATUS_COMPLETED)
        self.assertEqual(order.result, "CT normal")
        self.assertIsNotNone(order.completed_at)

    def test_emergency_profile_creation(self):
        user_e = User.objects.create_user(username="emergency1", password="password")
        emergency = EmergencyService.objects.create(user=user_e, role="EME")
        self.assertEqual(emergency.role, "EME")

    def test_document_is_encrypted_at_rest(self):
        user_u = User.objects.create_user(username="docuser", password="password")
        document = Document.objects.create(
            uploaded_by=user_u,
            file=SimpleUploadedFile("test.txt", b"secret payload", content_type="text/plain"),
            original_name="test.txt",
            encrypted=False,
        )

        self.assertEqual(document.uploaded_by.username, "docuser")
        self.assertTrue(document.encrypted)
        self.assertEqual(document.get_download_content(), b"secret payload")


@override_settings(MEDIA_ROOT="/tmp/heal-test-media")
class WorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username="admin1", password="password")
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        Administrator.objects.create(user=self.admin_user, level="Senior")

    def test_patient_registration_starts_pending(self):
        response = self.client.post(
            reverse("register_patient"),
            {
                "username": "pending_patient",
                "first_name": "Padme",
                "last_name": "Amidala",
                "email": "padme@example.com",
                "password": "secure-pass-123",
                "date_of_birth": "2000-01-01",
                "location": "Coruscant",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(Patient.objects.get(user__username="pending_patient").is_approved)

    def test_admin_can_approve_pending_doctor(self):
        user = User.objects.create_user(username="pending_doctor", password="password")
        doctor = Doctor.objects.create(user=user, specialty="Cardiology", is_approved=False)
        self.client.login(username="admin1", password="password")

        response = self.client.post(
            reverse("approve_user"),
            {"profile_type": "doctor", "profile_id": doctor.id},
        )

        self.assertRedirects(response, reverse("admin_monitoring"))
        doctor.refresh_from_db()
        self.assertTrue(doctor.is_approved)

    def test_unapproved_patient_cannot_add_reading(self):
        user = User.objects.create_user(username="pending_readings", password="password")
        Patient.objects.create(user=user, is_approved=False)
        self.client.login(username="pending_readings", password="password")

        response = self.client.get(reverse("add_reading"))

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(HealthReading.objects.count(), 0)

    def test_department_can_process_order(self):
        patient_user = User.objects.create_user(username="patient_order", password="password")
        patient = Patient.objects.create(user=patient_user, is_approved=True)
        doctor_user = User.objects.create_user(username="doctor_order", password="password")
        doctor = Doctor.objects.create(user=doctor_user, specialty="General", is_approved=True)
        department_user = User.objects.create_user(username="dep_process", password="password")
        Department.objects.create(user=department_user, department_name="Imaging")
        order = Order.objects.create(patient=patient, doctor=doctor, description="CT scan")
        self.client.login(username="dep_process", password="password")

        response = self.client.post(
            reverse("process_order", args=[order.id]),
            {"status": Order.STATUS_COMPLETED, "result": "Completed successfully"},
        )

        self.assertRedirects(response, reverse("dashboard"))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_COMPLETED)
        self.assertEqual(order.result, "Completed successfully")
        self.assertIsNotNone(order.completed_at)

    def test_document_download_returns_plaintext_for_owner(self):
        user = User.objects.create_user(username="doc_owner", password="password")
        Patient.objects.create(user=user, is_approved=True)
        document = Document.objects.create(
            uploaded_by=user,
            file=SimpleUploadedFile("lab.txt", b"lab result", content_type="text/plain"),
            original_name="lab.txt",
            encrypted=False,
        )
        self.client.login(username="doc_owner", password="password")

        response = self.client.get(reverse("download_document", args=[document.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"lab result")
