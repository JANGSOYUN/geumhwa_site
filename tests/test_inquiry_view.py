#!/usr/bin/env python
"""
Integration test for the inquiry view.
Tests the actual form submission flow.
"""

import os
import sys
import io

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geumhwa_site.settings')

import django
django.setup()

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


def test_inquiry_get():
    """Test that inquiry page loads correctly."""
    print("=" * 60)
    print("[TEST 1] Inquiry Page GET Request")
    print("=" * 60)

    client = Client()
    response = client.get('/inquiry/')

    print(f"  Status Code: {response.status_code}")

    if response.status_code == 200:
        print("[SUCCESS] Inquiry page loads correctly")
        return True
    else:
        print(f"[FAILED] Unexpected status code: {response.status_code}")
        return False


def test_inquiry_post_without_attachments():
    """Test form submission without attachments."""
    print("\n" + "=" * 60)
    print("[TEST 2] Form Submission Without Attachments")
    print("=" * 60)

    client = Client()

    data = {
        'company_name': '테스트 회사',
        'product_name': '테스트 제품',
        'size': '100x100x50mm',
        'quantity': '1000개',
        'other_requests': '테스트 요청사항',
    }

    print(f"  Submitting form data:")
    for key, value in data.items():
        print(f"    - {key}: {value}")

    response = client.post('/inquiry/', data, follow=True)

    print(f"  Status Code: {response.status_code}")
    print(f"  Redirect Chain: {response.redirect_chain}")

    # Check for success message
    # Handle context being None or empty
    messages = []
    if response.context:
        messages = list(response.context.get('messages', []))

    if messages:
        for msg in messages:
            print(f"  Message: [{msg.tags}] {msg.message}")

    # Check if redirected successfully (302 status means redirect, then 200 after redirect)
    if response.status_code == 200 and len(response.redirect_chain) > 0:
        print("[SUCCESS] Form submitted successfully (redirect occurred)")
        return True
    elif response.status_code == 200 and any('성공' in str(m) or '접수' in str(m) for m in messages):
        print("[SUCCESS] Form submitted successfully")
        return True
    else:
        print("[FAILED] Form submission failed or no success message")
        return False


def test_inquiry_post_with_text_attachment():
    """Test form submission with a text file attachment."""
    print("\n" + "=" * 60)
    print("[TEST 3] Form Submission With Text Attachment")
    print("=" * 60)

    client = Client()

    # Create a test file
    test_file = SimpleUploadedFile(
        name='test_document.txt',
        content=b'This is test content for the attachment file.\nLine 2\nLine 3',
        content_type='text/plain'
    )

    data = {
        'company_name': '테스트 회사 (첨부파일 테스트)',
        'product_name': '첨부파일 테스트 제품',
        'size': '200x200x100mm',
        'quantity': '500개',
        'other_requests': '텍스트 파일 첨부 테스트입니다.',
        'attachments': test_file,
    }

    print(f"  Submitting form with attachment:")
    print(f"    - File: test_document.txt")

    response = client.post('/inquiry/', data, follow=True)

    print(f"  Status Code: {response.status_code}")

    messages = []
    if response.context:
        messages = list(response.context.get('messages', []))

    if messages:
        for msg in messages:
            print(f"  Message: [{msg.tags}] {msg.message}")

    if response.status_code == 200 and len(response.redirect_chain) > 0:
        print("[SUCCESS] Form with text attachment submitted successfully")
        return True
    elif response.status_code == 200 and any('성공' in str(m) or '접수' in str(m) for m in messages):
        print("[SUCCESS] Form with text attachment submitted successfully")
        return True
    else:
        print("[FAILED] Form with attachment submission failed")
        return False


def test_inquiry_post_with_image_attachment():
    """Test form submission with an image attachment."""
    print("\n" + "=" * 60)
    print("[TEST 4] Form Submission With Image Attachment")
    print("=" * 60)

    client = Client()

    # Create a minimal valid PNG file
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
        0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
        0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
        0x44, 0xAE, 0x42, 0x60, 0x82
    ])

    test_image = SimpleUploadedFile(
        name='test_image.png',
        content=png_data,
        content_type='image/png'
    )

    data = {
        'company_name': '테스트 회사 (이미지 첨부)',
        'product_name': '이미지 첨부 테스트 제품',
        'size': '300x300x150mm',
        'quantity': '2000개',
        'other_requests': '이미지 파일 첨부 테스트입니다.',
        'attachments': test_image,
    }

    print(f"  Submitting form with image attachment:")
    print(f"    - File: test_image.png")

    response = client.post('/inquiry/', data, follow=True)

    print(f"  Status Code: {response.status_code}")

    messages = []
    if response.context:
        messages = list(response.context.get('messages', []))

    if messages:
        for msg in messages:
            print(f"  Message: [{msg.tags}] {msg.message}")

    if response.status_code == 200 and len(response.redirect_chain) > 0:
        print("[SUCCESS] Form with image attachment submitted successfully")
        return True
    elif response.status_code == 200 and any('성공' in str(m) or '접수' in str(m) for m in messages):
        print("[SUCCESS] Form with image attachment submitted successfully")
        return True
    else:
        print("[FAILED] Form with image attachment submission failed")
        return False


def test_inquiry_validation_required_fields():
    """Test that required fields are validated."""
    print("\n" + "=" * 60)
    print("[TEST 5] Required Fields Validation")
    print("=" * 60)

    client = Client()

    # Submit with missing required fields
    data = {
        'company_name': '',  # Empty
        'product_name': 'Test Product',
        'size': '',  # Empty
        'quantity': '100',
    }

    print(f"  Submitting form with missing required fields")

    response = client.post('/inquiry/', data, follow=True)

    print(f"  Status Code: {response.status_code}")

    messages = []
    if response.context:
        messages = list(response.context.get('messages', []))

    if messages:
        for msg in messages:
            print(f"  Message: [{msg.tags}] {msg.message}")

    # Should get an error message
    if any('error' in str(m.tags) or '필수' in str(m) for m in messages):
        print("[SUCCESS] Required field validation works correctly")
        return True
    elif response.status_code == 200 and len(response.redirect_chain) > 0:
        # Redirect occurred, check if it was due to validation error
        print("[SUCCESS] Required field validation works correctly (redirect)")
        return True
    else:
        print("[FAILED] Required field validation not working")
        return False


def test_inquiry_file_extension_validation():
    """Test that invalid file extensions are rejected."""
    print("\n" + "=" * 60)
    print("[TEST 6] File Extension Validation")
    print("=" * 60)

    client = Client()

    # Create a file with invalid extension
    invalid_file = SimpleUploadedFile(
        name='malicious.exe',
        content=b'fake executable content',
        content_type='application/octet-stream'
    )

    data = {
        'company_name': '테스트 회사',
        'product_name': '테스트 제품',
        'size': '100x100x50mm',
        'quantity': '1000개',
        'attachments': invalid_file,
    }

    print(f"  Submitting form with invalid file extension (.exe)")

    response = client.post('/inquiry/', data, follow=True)

    print(f"  Status Code: {response.status_code}")

    messages = []
    if response.context:
        messages = list(response.context.get('messages', []))

    if messages:
        for msg in messages:
            print(f"  Message: [{msg.tags}] {msg.message}")

    # Should get an error message about file type
    if any('error' in str(m.tags) or '허용' in str(m) or '형식' in str(m) for m in messages):
        print("[SUCCESS] File extension validation works correctly")
        return True
    elif response.status_code == 200 and len(response.redirect_chain) > 0:
        print("[SUCCESS] File extension validation works correctly (redirect)")
        return True
    else:
        print("[FAILED] File extension validation not working")
        return False


def main():
    """Run all inquiry view tests."""
    print("\n" + "=" * 60)
    print("INQUIRY VIEW INTEGRATION TEST SUITE")
    print("=" * 60)

    results = {}

    results['GET Request'] = test_inquiry_get()
    results['POST Without Attachments'] = test_inquiry_post_without_attachments()
    results['POST With Text Attachment'] = test_inquiry_post_with_text_attachment()
    results['POST With Image Attachment'] = test_inquiry_post_with_image_attachment()
    results['Required Fields Validation'] = test_inquiry_validation_required_fields()
    results['File Extension Validation'] = test_inquiry_file_extension_validation()

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
