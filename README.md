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
- streamlined self-registration for patients and doctors
- role-based dashboards and views for patient, doctor, department, admin, and emergency teams
- encrypted document upload/download for approved patients and doctors
- templates and forms for each major action
- admin site integration and CI for management quality

More specifically:
- Patients can register with only first name and last name required, land directly on the dashboard, upload daily readings, and view registered doctors.
- Doctors can register with only first name and last name required, land directly on the dashboard, inspect patient records, write reports, and create medical service orders.
- Department users can process orders and upload results.
- Emergency services can quickly create new patient entries and review critical patient records.
- Administrators can approve patient and doctor accounts, register users, and monitor activity from a dedicated dashboard.

## Deployed Application
- Live app: `https://coruscant-health-administration.onrender.com`
- Dashboard: `https://coruscant-health-administration.onrender.com/dashboard/`
- Admin monitoring: `https://coruscant-health-administration.onrender.com/admin/monitoring/`
- Emergency intake: `https://coruscant-health-administration.onrender.com/emergency/add-patient/`
- Login: `https://coruscant-health-administration.onrender.com/accounts/login/`

## Default Users
The application includes pre-configured users for different roles:

| Username | Password | Role              | Access Level                 |
|----------|----------|-------------------|------------------------------|
| EME      | EME      | Emergency Services| Critical patients and alerts |
| DEP1     | DEP      | Department User 1 | Orders and reports           |
| DEP2     | DEP      | Department User 2 | Orders and reports           |
| ADM1     | ADM      | Administrator 1   | Full system access           |
| ADM2     | ADM      | Administrator 2   | Full system access           |

Login at: `https://coruscant-health-administration.onrender.com/accounts/login/`

Notes:
- Default users are created automatically when the application home page is opened if they do not already exist.
- Patient and doctor self-registered accounts are approved immediately and redirected straight to the dashboard.
- Patient and doctor accounts created directly by an administrator are approved immediately.

## Features
- **Role-based access control** with different dashboards per user type
- **Fast self-registration** where public patient and doctor signup requires only first name and last name
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
- The dashboard and role panels show the signed-in user's first name and last name after registration.
- The patient dashboard also shows a list of registered doctors.
- A top ribbon identifies the project as an improved Qwasar project by Gints Turlajs.

## Review Corrections
The negative review points mentioned during grading have been corrected in this version:
- patient and doctor public registration no longer blocks progress behind extra required fields
- first name and last name are now the only required public registration fields
- valid registration now redirects directly to the next dashboard screen
- the registered first name and last name are now visible on the dashboard and role panel
- the patient dashboard now also displays the registered doctors list
- invalid first name or last name input now stays on the form and shows validation feedback

## Registration
- Register patient: `/register/patient/`
- Register doctor: `/register/doctor/`
- Dashboard: `/dashboard/`

Public registration behavior:
- Only `first_name` and `last_name` are required for patient and doctor signup.
- Optional fields can be left empty.
- After a valid submission, the user is logged in automatically and redirected to the dashboard.
- If first name or last name is missing or malformed, the form stays on the registration page and shows validation errors.

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

### The Core Team

The core team consists of Gints Turlajs and Gints Turlajs aka The Dream Team.

<span><i>Made at <a href='https://qwasar.io'>Qwasar SV -- Software Engineering School</a></i></span>
<span><img alt='Qwasar SV -- Software Engineering School's Logo' src='https://storage.googleapis.com/qwasar-public/qwasar-logo_50x50.png' width='20px' /></span>
