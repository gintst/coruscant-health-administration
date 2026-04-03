# Welcome to Coruscant Health Administration
***

## Task
This is a QWASAR task to rebuild the Coruscant Health Administration medical management system as a Django web application. The challenge is to support patient/doctor registration, device reading uploads, doctor reports, order processing, and a responsive UI + secure documents.

This implementation also covers the required stakeholder workflows for:
- Patient
- Doctor
- Department
- Administrator
- Emergency Services

## Description
The solution is a Django project (`cha`) with a `core` app that includes:
- `Patient` and `Doctor` profiles
- `HealthReading`, `Order`, `DoctorReport`, `Document` data models
- administrator approval workflow for patient and doctor onboarding
- role-based dashboards and views for patient, doctor, department, admin, and emergency teams
- encrypted document upload/download for approved patients and doctors
- templates and forms for each major action
- admin site integration and CI for management quality

More specifically:
- Patients can register, wait for administrator approval, upload daily readings, and view doctor suggestions.
- Doctors can register, wait for administrator approval, inspect patient records, write reports, and create medical service orders.
- Department users can process orders and upload results.
- Emergency services can quickly create new patient entries and review critical patient records.
- Administrators can approve patient and doctor accounts, register users, and monitor activity from a dedicated dashboard.

## Installation
1. Create and activate Python venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Installed project dependencies include:
- `Django==4.2`
- `cryptography==46.0.2`

3. Initialize database:

```bash
python manage.py migrate
```

Optional:
- Set `DOCUMENT_ENCRYPTION_SECRET` for a dedicated document-encryption key in addition to Django `SECRET_KEY`.

## Usage
Start the Django development server:

```bash
python manage.py runserver 0.0.0.0:8004
```

Open browser at:

```
http://127.0.0.1:8004/
```

Useful pages:
- Dashboard: `http://127.0.0.1:8004/dashboard/`
- Admin monitoring: `http://127.0.0.1:8004/admin/monitoring/`
- Django admin: `http://127.0.0.1:8004/django-admin/`
- Emergency intake: `http://127.0.0.1:8004/emergency/add-patient/`

## Default Users
The application includes pre-configured users for different roles:

| Username | Password | Role              | Access Level                 |
|----------|----------|-------------------|------------------------------|
| EME      | EME      | Emergency Services| Critical patients and alerts |
| DEP1     | DEP      | Department User 1 | Orders and reports           |
| DEP2     | DEP      | Department User 2 | Orders and reports           |
| ADM1     | ADM      | Administrator 1   | Full system access           |
| ADM2     | ADM      | Administrator 2   | Full system access           |

Login at: `http://127.0.0.1:8004/accounts/login/`

Notes:
- Default users are created automatically when the application home page is opened if they do not already exist.
- Patient and doctor self-registered accounts start pending approval until acknowledged by an administrator.
- Patient and doctor accounts created directly by an administrator are approved immediately.

## Features
- **Role-based access control** with different dashboards per user type
- **Administrator acknowledgment** before patients and doctors can perform protected actions
- **Emergency patient registration** for quick data entry
- **Department order processing** with structured order status tracking
- **Encrypted document storage** for patient and doctor uploads
- **Logout functionality** to switch between users
- **Responsive design** for all device types
- **GitHub Actions CI** for migrations and tests

Additional implemented behavior:
- Patient records can be viewed in a shared role-safe record page.
- Orders now include status, result text, and completion timestamp.
- Documents are encrypted before storage and only downloadable by the uploader or an administrator.
- A top ribbon identifies the project as a Qwasar project by Gints Turlajs.

## Registration
- Register patient: `/register/patient/`
- Register doctor: `/register/doctor/`
- Dashboard: `/dashboard/`

Additional role routes:
- Patient record: `/patient/<id>/record/`
- Submit report: `/patient/<id>/report/`
- Submit order: `/patient/<id>/order/`
- Process order: `/order/<id>/process/`
- Emergency add patient: `/emergency/add-patient/`
- Admin register user: `/admin/register-user/`
- Admin approve user: `/admin/approve-user/`
- Upload document: `/document/upload/`
- Download document: `/document/<id>/download/`
- Logout: `/accounts/logout/`

Testing:
- Run tests with `python manage.py test`
- CI workflow is defined in `.github/workflows/ci.yml`
- The automated test suite currently covers approval flow, order processing, and encrypted document handling.

Deployment note:
- The deployed cloud URL should be written in `my_coruscant_health_administration_url.txt`
- That file should contain only the final deployed URL

### The Core Team

The core team consists of Gints Turlajs and Gints Turlajs aka The Dream Team.

<span><i>Made at <a href='https://qwasar.io'>Qwasar SV -- Software Engineering School</a></i></span>
<span><img alt='Qwasar SV -- Software Engineering School's Logo' src='https://storage.googleapis.com/qwasar-public/qwasar-logo_50x50.png' width='20px' /></span>
