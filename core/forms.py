import re

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


class PublicRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)

    name_pattern = re.compile(r"^[A-Za-z][A-Za-z '\-]*[A-Za-z]$|^[A-Za-z]$")

    def _clean_name_field(self, field_name):
        value = (self.cleaned_data.get(field_name) or "").strip()
        if not value:
            raise forms.ValidationError("This field is required.")
        if not self.name_pattern.fullmatch(value):
            raise forms.ValidationError("Use letters only, with spaces, apostrophes, or hyphens if needed.")
        return value

    def clean_first_name(self):
        return self._clean_name_field("first_name")

    def clean_last_name(self):
        return self._clean_name_field("last_name")


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
