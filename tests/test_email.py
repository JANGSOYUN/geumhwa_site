#!/usr/bin/env python
"""
Email functionality test script for geumhwa_site.
Tests basic email sending, attachments, and SMTP connection.
"""

import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geumhwa_site.settings')

import django
django.setup()

from django.core.mail import send_mail, EmailMessage, get_connection
from django.conf import settings


def test_smtp_connection():
    """Test SMTP connection to Gmail."""
    print("=" * 60)
    print("[TEST 1] SMTP Connection Test")
    print("=" * 60)

    try:
        connection = get_connection()
        connection.open()
        print(f"[SUCCESS] Connected to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"  - TLS: {settings.EMAIL_USE_TLS}")
        print(f"  - User: {settings.EMAIL_HOST_USER}")
        connection.close()
        return True
    except Exception as e:
        print(f"[FAILED] Connection error: {str(e)}")
        return False


def test_basic_email():
    """Test sending a basic email without attachments."""
    print("\n" + "=" * 60)
    print("[TEST 2] Basic Email Test (No Attachments)")
    print("=" * 60)

    subject = "[TEST] Basic Email Test"
    message = """This is a test email from geumhwa_site.

Test Details:
- Test Type: Basic email without attachments
- Sender: {sender}
- Time: Now

If you received this email, the basic email functionality is working.
""".format(sender=settings.EMAIL_HOST_USER)

    recipient = settings.EMAIL_HOST_USER  # Send to self for testing

    try:
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )

        if result == 1:
            print(f"[SUCCESS] Email sent successfully!")
            print(f"  - To: {recipient}")
            print(f"  - Subject: {subject}")
            return True
        else:
            print(f"[FAILED] send_mail returned {result}")
            return False
    except Exception as e:
        print(f"[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_email_with_single_attachment():
    """Test sending an email with a single text attachment."""
    print("\n" + "=" * 60)
    print("[TEST 3] Email with Single Attachment")
    print("=" * 60)

    subject = "[TEST] Email with Single Attachment"
    message = """This is a test email with a single attachment.

If you received this email with an attached file, the attachment functionality is working.
"""
    recipient = settings.EMAIL_HOST_USER

    # Create a test file
    test_content = b"This is test content for the attachment.\nLine 2\nLine 3"

    try:
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )

        # Attach test file
        email.attach('test_file.txt', test_content, 'text/plain')

        print(f"  - Attachments count: {len(email.attachments)}")
        for name, content, mime in email.attachments:
            print(f"    * {name} ({mime}), size: {len(content)} bytes")

        result = email.send()

        if result == 1:
            print(f"[SUCCESS] Email with attachment sent!")
            return True
        else:
            print(f"[FAILED] send returned {result}")
            return False
    except Exception as e:
        print(f"[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_email_with_binary_attachment():
    """Test sending an email with a binary (image-like) attachment."""
    print("\n" + "=" * 60)
    print("[TEST 4] Email with Binary Attachment (Image)")
    print("=" * 60)

    subject = "[TEST] Email with Binary Attachment"
    message = """This is a test email with a binary attachment (simulated image).

If you received this email with the attachment, binary file handling is working.
"""
    recipient = settings.EMAIL_HOST_USER

    # Create a minimal valid PNG file (1x1 pixel, red)
    # PNG signature + IHDR chunk + IDAT chunk + IEND chunk
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk length and type
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # Width=1, Height=1
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # Bit depth, color type, etc.
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
        0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
        0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
        0x44, 0xAE, 0x42, 0x60, 0x82
    ])

    try:
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )

        email.attach('test_image.png', png_data, 'image/png')

        print(f"  - Attachments count: {len(email.attachments)}")
        for name, content, mime in email.attachments:
            print(f"    * {name} ({mime}), size: {len(content)} bytes")

        result = email.send()

        if result == 1:
            print(f"[SUCCESS] Email with binary attachment sent!")
            return True
        else:
            print(f"[FAILED] send returned {result}")
            return False
    except Exception as e:
        print(f"[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_email_with_multiple_attachments():
    """Test sending an email with multiple attachments."""
    print("\n" + "=" * 60)
    print("[TEST 5] Email with Multiple Attachments")
    print("=" * 60)

    subject = "[TEST] Email with Multiple Attachments"
    message = """This is a test email with multiple attachments.

If you received this email with all attachments, multiple file handling is working.
"""
    recipient = settings.EMAIL_HOST_USER

    try:
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )

        # Attach multiple files
        email.attach('file1.txt', b'Content of file 1', 'text/plain')
        email.attach('file2.txt', b'Content of file 2 with more text', 'text/plain')
        email.attach('file3.txt', b'Content of file 3', 'text/plain')

        print(f"  - Attachments count: {len(email.attachments)}")
        for name, content, mime in email.attachments:
            print(f"    * {name} ({mime}), size: {len(content)} bytes")

        result = email.send()

        if result == 1:
            print(f"[SUCCESS] Email with multiple attachments sent!")
            return True
        else:
            print(f"[FAILED] send returned {result}")
            return False
    except Exception as e:
        print(f"[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_inquiry_email_simulation():
    """Simulate the actual inquiry email format."""
    print("\n" + "=" * 60)
    print("[TEST 6] Inquiry Email Simulation")
    print("=" * 60)

    # Simulate inquiry form data
    company_name = "테스트 회사"
    product_name = "테스트 제품"
    size = "100x100x50mm"
    quantity = "1000개"
    other_requests = "테스트 요청사항입니다."

    subject = f'[견적문의] {company_name} - {product_name}'
    message = f'''견적문의가 접수되었습니다.

회사명: {company_name}
제품명: {product_name}
사이즈(형태): {size}
수량: {quantity}
기타 요청사항: {other_requests}

첨부파일: 1개
  - test_attachment.txt (0.00MB)
'''

    recipient = settings.EMAIL_HOST_USER

    try:
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )

        # Attach a test file
        email.attach('test_attachment.txt', b'Test attachment content', 'text/plain')

        print(f"  - Subject: {subject}")
        print(f"  - To: {recipient}")
        print(f"  - Attachments: {len(email.attachments)}")

        result = email.send()

        if result == 1:
            print(f"[SUCCESS] Inquiry simulation email sent!")
            return True
        else:
            print(f"[FAILED] send returned {result}")
            return False
    except Exception as e:
        print(f"[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all email tests."""
    print("\n" + "=" * 60)
    print("GEUMHWA EMAIL FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email User: {settings.EMAIL_HOST_USER}")
    print(f"TLS Enabled: {settings.EMAIL_USE_TLS}")
    print("=" * 60)

    results = {}

    # Run tests
    results['SMTP Connection'] = test_smtp_connection()

    if results['SMTP Connection']:
        results['Basic Email'] = test_basic_email()
        results['Single Attachment'] = test_email_with_single_attachment()
        results['Binary Attachment'] = test_email_with_binary_attachment()
        results['Multiple Attachments'] = test_email_with_multiple_attachments()
        results['Inquiry Simulation'] = test_inquiry_email_simulation()
    else:
        print("\n[SKIPPED] Skipping email tests due to SMTP connection failure")
        results['Basic Email'] = False
        results['Single Attachment'] = False
        results['Binary Attachment'] = False
        results['Multiple Attachments'] = False
        results['Inquiry Simulation'] = False

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
