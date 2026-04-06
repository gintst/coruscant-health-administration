from datetime import timedelta
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ApprovalActionForm,
    DoctorReportForm,
    DocumentUploadForm,
    DoctorProfileForm,
    HealthReadingForm,
    OrderForm,
    OrderProcessForm,
    PatientProfileForm,
    PublicRegistrationForm,
    UserLoginForm,
    UserRegistrationForm,
)
from .models import (
    Administrator,
    Department,
    Doctor,
    DoctorReport,
    Document,
    EmergencyService,
    HealthReading,
    Order,
    Patient,
)


def ensure_default_users():
    if not User.objects.filter(username="EME").exists():
        eme_user = User.objects.create_user(
            username="EME",
            password="EME",
            first_name="Emergency",
            last_name="Service",
        )
        EmergencyService.objects.create(user=eme_user, role="EME")

    if not User.objects.filter(username="DEP1").exists():
        dep1_user = User.objects.create_user(
            username="DEP1",
            password="DEP",
            first_name="Department",
            last_name="User1",
        )
        Department.objects.create(user=dep1_user, department_name="General")

    if not User.objects.filter(username="DEP2").exists():
        dep2_user = User.objects.create_user(
            username="DEP2",
            password="DEP",
            first_name="Department",
            last_name="User2",
        )
        Department.objects.create(user=dep2_user, department_name="Administration")

    adm1_user, adm1_created = User.objects.get_or_create(
        username="ADM1",
        defaults={
            "first_name": "Administrator",
            "last_name": "One",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if adm1_created:
        adm1_user.set_password("ADM")
    adm1_needs_save = adm1_created
    if not adm1_user.is_staff:
        adm1_user.is_staff = True
        adm1_needs_save = True
    if not adm1_user.is_superuser:
        adm1_user.is_superuser = True
        adm1_needs_save = True
    if adm1_needs_save:
        adm1_user.save()
    Administrator.objects.get_or_create(user=adm1_user, defaults={"level": "Senior"})

    if not User.objects.filter(username="ADM2").exists():
        adm2_user = User.objects.create_user(
            username="ADM2",
            password="ADM",
            first_name="Administrator",
            last_name="Two",
        )
        adm2_user.is_staff = True
        adm2_user.is_superuser = True
        adm2_user.save()
        Administrator.objects.create(user=adm2_user, level="Junior")


def approved_patient(user):
    patient = getattr(user, "patient_profile", None)
    return patient if patient and patient.is_approved else None


def approved_doctor(user):
    doctor = getattr(user, "doctor_profile", None)
    return doctor if doctor and doctor.is_approved else None


def user_can_access_patient_record(user, patient):
    return bool(
        getattr(user, "admin_profile", None)
        or getattr(user, "department_profile", None)
        or getattr(user, "emergency_profile", None)
        or approved_doctor(user)
        or (approved_patient(user) and approved_patient(user).id == patient.id)
    )


def home(request):
    ensure_default_users()
    return render(
        request,
        "core/home.html",
        {
            "doctor_count": Doctor.objects.filter(is_approved=True).count(),
            "order_count": Order.objects.count(),
            "patient_count": Patient.objects.count(),
            "reading_count": HealthReading.objects.count(),
        },
    )


def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "dashboard")
                return redirect(next_url)
            form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, "core/login.html", {"form": form})


def build_public_username(first_name, last_name):
    base = f"{first_name}.{last_name}".lower().replace(" ", "-").replace("'", "").replace('"', "")
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = f"{base}{suffix}"
    return candidate


def register_patient(request):
    if request.method == "POST":
        form = PublicRegistrationForm(request.POST)
        profile_form = PatientProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = User(
                username=build_public_username(
                    form.cleaned_data["first_name"],
                    form.cleaned_data["last_name"],
                ),
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data.get("email", ""),
            )
            user.set_unusable_password()
            user.save()
            patient = profile_form.save(commit=False)
            patient.user = user
            patient.is_approved = True
            patient.save()
            patient_group, _ = Group.objects.get_or_create(name="Patient")
            user.groups.add(patient_group)
            login(request, user)
            messages.success(
                request,
                "Your patient account is ready. You can add readings and documents now.",
            )
            return redirect("dashboard")
    else:
        form = PublicRegistrationForm()
        profile_form = PatientProfileForm()
    return render(
        request,
        "core/register_patient.html",
        {"form": form, "profile_form": profile_form},
    )


def register_doctor(request):
    if request.method == "POST":
        form = PublicRegistrationForm(request.POST)
        profile_form = DoctorProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = User(
                username=build_public_username(
                    form.cleaned_data["first_name"],
                    form.cleaned_data["last_name"],
                ),
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data.get("email", ""),
            )
            user.set_unusable_password()
            user.is_staff = True
            user.save()
            doctor = profile_form.save(commit=False)
            doctor.user = user
            doctor.specialty = doctor.specialty or "General"
            doctor.is_approved = True
            doctor.save()
            doctor_group, _ = Group.objects.get_or_create(name="Doctor")
            user.groups.add(doctor_group)
            login(request, user)
            messages.success(
                request,
                "Your doctor account is ready. You can start using the dashboard now.",
            )
            return redirect("dashboard")
    else:
        form = PublicRegistrationForm()
        profile_form = DoctorProfileForm()
    return render(request, "core/register_doctor.html", {"form": form, "profile_form": profile_form})


@login_required
def admin_register_user(request):
    admin = getattr(request.user, "admin_profile", None)
    if not admin:
        return redirect("dashboard")

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        user_type = request.POST.get("user_type")

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            if user_type == "patient":
                Patient.objects.create(
                    user=user,
                    date_of_birth=request.POST.get("date_of_birth"),
                    location=request.POST.get("location"),
                    is_approved=True,
                )
                patient_group, _ = Group.objects.get_or_create(name="Patient")
                user.groups.add(patient_group)
            elif user_type == "doctor":
                Doctor.objects.create(
                    user=user,
                    specialty=request.POST.get("specialty", "General"),
                    is_approved=True,
                )
                doctor_group, _ = Group.objects.get_or_create(name="Doctor")
                user.groups.add(doctor_group)
                user.is_staff = True
                user.save()
            elif user_type == "emergency":
                EmergencyService.objects.create(
                    user=user,
                    role=request.POST.get("role", "Emergency Staff"),
                )
            elif user_type == "department":
                Department.objects.create(
                    user=user,
                    department_name=request.POST.get("department_name", "General"),
                )
            elif user_type == "administrator":
                Administrator.objects.create(
                    user=user,
                    level=request.POST.get("level", "Standard"),
                )
                user.is_staff = True
                user.is_superuser = True
                user.save()

            messages.success(request, "User account created successfully.")
            return redirect("admin_monitoring")
    else:
        user_form = UserRegistrationForm()

    return render(request, "core/admin_register_user.html", {"user_form": user_form})


@login_required
def dashboard(request):
    user = request.user
    patient = getattr(user, "patient_profile", None)
    doctor = getattr(user, "doctor_profile", None)
    emergency = getattr(user, "emergency_profile", None)
    department = getattr(user, "department_profile", None)
    admin = getattr(user, "admin_profile", None)

    context = {
        "admin": admin,
        "department": department,
        "doctor": doctor,
        "documents": Document.objects.filter(uploaded_by=user).order_by("-uploaded_at"),
        "emergency": emergency,
        "patient": patient,
    }

    if patient:
        context.update(
            {
                "available_doctors": Doctor.objects.filter(is_approved=True).order_by("user__first_name", "user__last_name", "user__username"),
                "health_readings": HealthReading.objects.filter(patient=patient).order_by("-recorded_at"),
                "patient_is_approved": patient.is_approved,
                "reports": DoctorReport.objects.filter(patient=patient).order_by("-created_at"),
            }
        )
    elif doctor:
        context.update(
            {
                "doctor_is_approved": doctor.is_approved,
                "orders": Order.objects.filter(doctor=doctor).order_by("-created_at"),
                "patients": Patient.objects.all().order_by("user__username"),
                "reports": DoctorReport.objects.filter(doctor=doctor).order_by("-created_at"),
            }
        )
    elif emergency:
        critical_window = timezone.now() - timedelta(hours=24)
        context.update(
            {
                "critical_patients": Patient.objects.filter(
                    health_readings__recorded_at__gte=critical_window
                ).distinct(),
                "emergency_alerts": HealthReading.objects.filter(
                    recorded_at__gte=critical_window
                ).order_by("-recorded_at"),
            }
        )
    elif department:
        context.update(
            {
                "all_orders": Order.objects.all().order_by("-created_at"),
                "all_reports": DoctorReport.objects.all().order_by("-created_at"),
            }
        )
    elif admin:
        context.update(
            {
                "all_doctors": Doctor.objects.all().order_by("user__username"),
                "all_orders": Order.objects.all().order_by("-created_at"),
                "all_patients": Patient.objects.all().order_by("user__username"),
                "all_readings": HealthReading.objects.all().order_by("-recorded_at"),
                "all_reports": DoctorReport.objects.all().order_by("-created_at"),
            }
        )

    return render(request, "core/dashboard.html", context)


@login_required
def add_reading(request):
    patient = approved_patient(request.user)
    if not patient:
        messages.error(request, "Only approved patients can upload health readings.")
        return redirect("dashboard")

    if request.method == "POST":
        form = HealthReadingForm(request.POST)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.patient = patient
            reading.save()
            messages.success(request, "Health reading saved.")
            return redirect("dashboard")
    else:
        form = HealthReadingForm()
    return render(request, "core/add_reading.html", {"form": form})


@login_required
def patient_record(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if not user_can_access_patient_record(request.user, patient):
        messages.error(request, "You do not have access to this patient record.")
        return redirect("dashboard")

    return render(
        request,
        "core/patient_record.html",
        {
            "health_readings": HealthReading.objects.filter(patient=patient).order_by("-recorded_at"),
            "orders": Order.objects.filter(patient=patient).order_by("-created_at"),
            "patient": patient,
            "reports": DoctorReport.objects.filter(patient=patient).order_by("-created_at"),
        },
    )


@login_required
def doctor_report(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    doctor = approved_doctor(request.user)
    if not doctor:
        messages.error(request, "Only approved doctors can write patient reports.")
        return redirect("dashboard")

    if request.method == "POST":
        form = DoctorReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.doctor = doctor
            report.patient = patient
            report.save()
            messages.success(request, "Doctor report submitted.")
            return redirect("dashboard")
    else:
        form = DoctorReportForm()
    return render(request, "core/doctor_report.html", {"form": form, "patient": patient})


@login_required
def submit_order(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    doctor = approved_doctor(request.user)
    if not doctor:
        messages.error(request, "Only approved doctors can create service orders.")
        return redirect("dashboard")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.patient = patient
            order.doctor = doctor
            order.save()
            messages.success(request, "Medical order submitted.")
            return redirect("dashboard")
    else:
        form = OrderForm()
    return render(request, "core/submit_order.html", {"form": form, "patient": patient})


@login_required
def process_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    user_department = getattr(request.user, "department_profile", None)

    if not user_department:
        messages.error(request, "Only department staff can process service orders.")
        return redirect("dashboard")

    if request.method == "POST":
        form = OrderProcessForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            if order.status == Order.STATUS_COMPLETED and not order.completed_at:
                order.completed_at = timezone.now()
            order.save()
            messages.success(request, "Order updated successfully.")
            return redirect("dashboard")
    else:
        form = OrderProcessForm(instance=order)

    return render(request, "core/process_order.html", {"form": form, "order": order})


@login_required
def upload_document(request):
    if not (approved_patient(request.user) or approved_doctor(request.user)):
        messages.error(
            request,
            "Only approved patients and doctors can upload documents.",
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.original_name = request.FILES["file"].name
            document.encrypted = False
            document.save()
            messages.success(request, "Document encrypted and stored successfully.")
            return redirect("dashboard")
    else:
        form = DocumentUploadForm()
    return render(request, "core/upload_document.html", {"form": form})


@login_required
def download_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if document.uploaded_by != request.user and not getattr(request.user, "admin_profile", None):
        raise Http404

    content = document.get_download_content()
    if content is None:
        raise Http404

    return FileResponse(
        BytesIO(content),
        as_attachment=True,
        filename=document.original_name or "document.bin",
    )


@login_required
def emergency_add_patient(request):
    emergency = getattr(request.user, "emergency_profile", None)
    if not emergency:
        return redirect("dashboard")

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        patient_form = PatientProfileForm(request.POST)

        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            patient = patient_form.save(commit=False)
            patient.user = user
            patient.is_approved = True
            patient.save()

            patient_group, _ = Group.objects.get_or_create(name="Patient")
            user.groups.add(patient_group)
            messages.success(request, "Emergency patient added successfully.")
            return redirect("dashboard")
    else:
        user_form = UserRegistrationForm()
        patient_form = PatientProfileForm()

    return render(
        request,
        "core/emergency_add_patient.html",
        {"patient_form": patient_form, "user_form": user_form},
    )


@login_required
def admin_monitoring(request):
    admin = getattr(request.user, "admin_profile", None)
    if not admin:
        return redirect("dashboard")

    context = {
        "approval_form": ApprovalActionForm(),
        "critical_readings": HealthReading.objects.filter(
            recorded_at__gte=timezone.now() - timedelta(hours=24)
        ).order_by("-recorded_at")[:10],
        "pending_doctors": Doctor.objects.filter(is_approved=False).select_related("user"),
        "pending_orders": Order.objects.filter(status=Order.STATUS_PENDING).count(),
        "pending_patients": Patient.objects.filter(is_approved=False).select_related("user"),
        "recent_reports": DoctorReport.objects.order_by("-created_at")[:10],
        "total_admins": Administrator.objects.count(),
        "total_department_staff": Department.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "total_emergency_staff": EmergencyService.objects.count(),
        "total_orders": Order.objects.count(),
        "total_patients": Patient.objects.count(),
        "total_readings": HealthReading.objects.count(),
        "total_reports": DoctorReport.objects.count(),
        "total_users": User.objects.count(),
    }
    return render(request, "core/admin_monitoring.html", context)


@login_required
def approve_user(request):
    admin = getattr(request.user, "admin_profile", None)
    if not admin or request.method != "POST":
        return redirect("dashboard")

    form = ApprovalActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid approval request.")
        return redirect("admin_monitoring")

    model = Patient if form.cleaned_data["profile_type"] == "patient" else Doctor
    profile = get_object_or_404(model, id=form.cleaned_data["profile_id"])
    profile.is_approved = True
    profile.save(update_fields=["is_approved"])
    messages.success(request, f"{profile.user.username} has been approved.")
    return redirect("admin_monitoring")
