# GEUMHWA BOX Website Architecture

## Project Overview

- **Project Name:** geumhwa_site
- **Framework:** Django 5.2.x
- **Database:** SQLite3
- **Language:** Python

## Directory Structure

```
geumhwa_site/
├── geumhwa_site/           # Django project configuration
│   ├── settings.py         # Main configuration
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── main/                   # Main Django app
│   ├── views.py            # Views (includes inquiry/email)
│   ├── models.py           # Database models
│   ├── admin.py            # Admin configuration
│   ├── urls.py             # App URL routing
│   └── templates/main/     # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── tests/                  # Test scripts
├── db.sqlite3              # SQLite database
└── manage.py               # Django management script
```

## URL Routes

| URL | View | Description |
|-----|------|-------------|
| `/` | home | Homepage |
| `/company/` | company | Company information |
| `/products/` | products | Products overview |
| `/products/paper-box/` | paper_box | Paper box products |
| `/products/carton_box/` | carton_box | Carton box products |
| `/products/color_box/` | color_box | Color box products |
| `/equipment/` | equipment | Equipment page |
| `/inquiry/` | inquiry | Quote inquiry form |
| `/admin/` | Django admin | Admin interface |

## Email Configuration

### Settings (settings.py)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "geumhwa9300@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "...")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### Email Flow

1. User submits inquiry form at `/inquiry/`
2. Form data validated (required fields, file size, file types)
3. Email composed with inquiry details
4. If attachments exist: Use `EmailMessage` class
5. If no attachments: Use `send_mail()` function
6. Email sent via Gmail SMTP
7. Success/error message displayed to user

### Attachment Validation Rules

- Max file size: 10MB per file
- Max total size: 20MB for all files
- Max files: 3
- Allowed extensions: .pdf, .doc, .docx, .xls, .xlsx, .jpg, .jpeg, .png, .zip

## Testing

### Run Email Tests

```bash
cd D:\geumhwa_site
source venv/Scripts/activate  # Windows with Git Bash
python tests/test_email.py
python tests/test_inquiry_view.py
```

### Test Coverage

- [x] Basic email sending (without attachments)
- [x] Email sending with single attachment
- [x] Email sending with multiple attachments
- [x] Email sending with binary attachments (images)
- [x] File validation (size, type, count)
- [x] SMTP connection verification
- [x] Inquiry form GET request
- [x] Inquiry form POST with/without attachments
- [x] Required fields validation
- [x] File extension validation

## Email Functionality Status (Verified 2026-02-01)

| Feature | Status | Notes |
|---------|--------|-------|
| SMTP Connection | WORKING | Gmail SMTP port 587 with TLS |
| Basic email | WORKING | send_mail() function |
| Single attachment | WORKING | EmailMessage class |
| Multiple attachments | WORKING | Up to 3 files |
| Binary attachments (images) | WORKING | PNG, JPG, etc. |
| File validation | WORKING | Client and server-side |
| Korean text support | WORKING | UTF-8 encoding |

### Test Results Summary

```
GEUMHWA EMAIL FUNCTIONALITY TEST SUITE
============================================================
  SMTP Connection: PASSED
  Basic Email: PASSED
  Single Attachment: PASSED
  Binary Attachment: PASSED
  Multiple Attachments: PASSED
  Inquiry Simulation: PASSED
============================================================
Total: 6 passed, 0 failed

INQUIRY VIEW INTEGRATION TEST SUITE
============================================================
  GET Request: PASSED
  POST Without Attachments: PASSED
  POST With Text Attachment: PASSED
  POST With Image Attachment: PASSED
  Required Fields Validation: PASSED
  File Extension Validation: PASSED
============================================================
Total: 6 passed, 0 failed
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | dev key |
| `EMAIL_HOST_USER` | Gmail address | geumhwa9300@gmail.com |
| `EMAIL_HOST_PASSWORD` | Gmail app password | (configured) |
| `USE_S3` | Enable S3 storage | "0" (disabled) |

## Dependencies

- Django 5.2.x
- whitenoise (static file serving)
- django-storages (S3 support, optional)

## Debugging

### Email Debug File

When emails with attachments are sent, the MIME message structure is saved to:
```
D:\geumhwa_site\email_debug.txt
```

This file contains the raw email content including:
- MIME boundaries
- Content-Type headers
- Base64 encoded attachments

### Console Logging

Email operations are logged to console with `[DEBUG]` prefix showing:
- Attachment count and details
- File reading progress
- MIME structure verification
- Send success/failure status
