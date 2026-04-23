from django.contrib.messages import get_messages
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase, override_settings
from django.urls import reverse


class FailingEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise RuntimeError('SMTP authentication failed')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_HOST_USER='jangwkd@gmail.com',
    EMAIL_HOST_PASSWORD='fake-app-password',
    DEFAULT_FROM_EMAIL='jangwkd@gmail.com',
    INQUIRY_RECIPIENT_EMAILS=['jangwkd@gmail.com'],
)
class InquiryViewTests(TestCase):
    def setUp(self):
        self.url = reverse('inquiry')

    def _payload(self):
        return {
            'company_name': '테스트회사',
            'product_name': '테스트제품',
            'size': '100x100x50mm',
            'quantity': '1000개',
            'other_requests': '테스트 요청사항',
        }

    def _message_texts(self, response):
        return [message.message for message in get_messages(response.wsgi_request)]

    def test_inquiry_page_loads(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_post_sends_email_to_configured_recipient(self):
        response = self.client.post(self.url, self._payload(), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['jangwkd@gmail.com'])
        self.assertEqual(mail.outbox[0].from_email, 'jangwkd@gmail.com')
        self.assertIn('[견적문의] 테스트회사 - 테스트제품', mail.outbox[0].subject)
        self.assertIn('견적문의가 성공적으로 전송되었습니다.', self._message_texts(response))

    def test_post_with_attachment_includes_uploaded_file(self):
        attachment = SimpleUploadedFile(
            'spec.pdf',
            b'%PDF-1.4 test attachment',
            content_type='application/pdf',
        )

        response = self.client.post(
            self.url,
            {**self._payload(), 'attachments': attachment},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], 'spec.pdf')
        self.assertIn('견적문의가 성공적으로 전송되었습니다.', self._message_texts(response))

    def test_required_fields_are_validated(self):
        response = self.client.post(
            self.url,
            {
                'company_name': '',
                'product_name': '테스트제품',
                'size': '',
                'quantity': '1000개',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('필수 항목을 모두 입력해주세요.', self._message_texts(response))

    def test_invalid_file_extension_is_rejected(self):
        invalid_file = SimpleUploadedFile(
            'malicious.exe',
            b'fake executable content',
            content_type='application/octet-stream',
        )

        response = self.client.post(
            self.url,
            {**self._payload(), 'attachments': invalid_file},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any('허용되지 않는 파일 형식입니다.' in message for message in self._message_texts(response))
        )

    @override_settings(
        EMAIL_BACKEND='tests.test_inquiry_view.FailingEmailBackend',
        EMAIL_HOST_USER='jangwkd@gmail.com',
        EMAIL_HOST_PASSWORD='fake-app-password',
        DEFAULT_FROM_EMAIL='jangwkd@gmail.com',
        INQUIRY_RECIPIENT_EMAILS=['jangwkd@gmail.com'],
    )
    def test_email_failure_shows_error_message(self):
        response = self.client.post(self.url, self._payload(), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '견적문의 이메일 전송에 실패했습니다. 이메일 설정을 확인한 뒤 다시 시도해주세요.',
            self._message_texts(response),
        )
