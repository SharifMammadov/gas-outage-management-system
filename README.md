# Gas Outage Management System

A desktop application for recording, monitoring, and reporting gas service
interruptions and restorations. The project demonstrates how an operational
workflow can be translated into a role-based desktop system.

This public portfolio edition uses local SQLite storage and anonymized demo
accounts. It contains no production database, internal network configuration,
customer records, employee records, or proprietary brand assets.

## Features

- Role-based access for administrators, managers, and read-only users
- Interruption and restoration record management
- Status tracking: closed, restored, and stopped
- District, date, and status filters
- Operational reports and summary indicators
- Office, district, and reason reference lists
- Local backup support
- Azerbaijani and English interface with a persistent language selector
- Light and dark interface themes
- Input validation and automated model tests

## Tech stack

- Python 3.10+
- PyQt6
- SQLite
- `unittest`
- PyInstaller

## Getting started

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

Install and run:

```bash
pip install -r requirements.txt
python main.py
```

The application creates its local database automatically in `data/`.

## Demo accounts

| Role | Username | Password | Access |
| --- | --- | --- | --- |
| Administrator | `admin` | `demo123` | Full access |
| Manager | `manager` | `demo123` | Operational editing |
| Viewer | `viewer` | `demo123` | Read-only access |

Demo passwords are stored as salted PBKDF2 hashes in the generated local
database. They are intended only for local evaluation of this portfolio app.

## Tests

```bash
python run_tests.py
```

## Build a Windows executable

```powershell
pip install pyinstaller
build_exe.bat
```

## Project structure

```text
controllers/  Application controllers
models/       SQLite access and domain models
tests/        Automated tests
utils/        Validation, permissions, sessions, backups, and themes
views/        PyQt6 windows, dialogs, and tabs
main.py       Application entry point
```

## Portfolio note

Developed by **Sharif Mammadov** as a portfolio-safe demonstration of desktop
application development and workflow automation experience. The public edition
is independently presented with anonymized sample configuration and generic
branding.
