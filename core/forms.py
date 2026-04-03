from django import forms
from django.contrib.auth.models import User

from .models import Doctor, DoctorReport, HealthReading, Order, Patient, Document


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["date_of_birth", "location"]


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["specialty"]


class HealthReadingForm(forms.ModelForm):
    class Meta:
        model = HealthReading
        fields = ["heart_rate", "blood_pressure", "oxygen_saturation", "note"]


class DoctorReportForm(forms.ModelForm):
    class Meta:
        model = DoctorReport
        fields = ["report_text"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["description"]


class OrderProcessForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "result"]


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file"]


class ApprovalActionForm(forms.Form):
    profile_type = forms.ChoiceField(choices=[("patient", "Patient"), ("doctor", "Doctor")])
    profile_id = forms.IntegerField(min_value=1)
