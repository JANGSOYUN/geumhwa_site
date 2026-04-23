from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
import logging
import os


logger = logging.getLogger(__name__)


def _get_inquiry_recipients():
    recipients = getattr(settings, 'INQUIRY_RECIPIENT_EMAILS', None)
    if isinstance(recipients, str):
        recipients = recipients.split(',')

    normalized = [email.strip() for email in (recipients or []) if email and email.strip()]
    if not normalized:
        fallback_email = getattr(settings, 'EMAIL_HOST_USER', '').strip()
        if fallback_email:
            normalized = [fallback_email]

    if not normalized:
        raise ValueError('견적문의 수신 이메일이 설정되지 않았습니다.')

    return normalized


def _build_inquiry_email(subject, message, validated_attachments):
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
        _get_inquiry_recipients(),
    )

    for attachment in validated_attachments:
        attachment['file'].seek(0)
        email.attach(
            attachment['name'],
            attachment['file'].read(),
            attachment['content_type'],
        )
        attachment['file'].seek(0)

    return email


def robots_txt(request):
    """Serve robots.txt for search engine crawlers."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "Sitemap: https://www.geumhwabox.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def home(request):
    return render(request, 'main/index.html')

def company(request):
    return render(request, 'main/company.html')

def products(request):
    return render(request, 'main/products.html')

def paper_box(request):
    return render(request, 'main/paper_box.html')

def carton_box(request):
    return render(request, 'main/carton_box.html')

def color_box(request):
    return render(request, 'main/color_box.html')

def equipment(request):
    return render(request, 'main/equipment.html')

def inquiry(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name', '')
        product_name = request.POST.get('product_name', '')
        size = request.POST.get('size', '')
        quantity = request.POST.get('quantity', '')
        other_requests = request.POST.get('other_requests', '')
        attachments = request.FILES.getlist('attachments')
        
        # 필수 필드 검증
        if not company_name or not product_name or not size or not quantity:
            messages.error(request, '필수 항목을 모두 입력해주세요.')
            return redirect('inquiry')
        
        # 첨부파일 검증
        max_file_size = 10 * 1024 * 1024  # 10MB
        max_total_size = 20 * 1024 * 1024  # 20MB
        max_files = 3
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip']
        
        if len(attachments) > max_files:
            messages.error(request, f'첨부파일은 최대 {max_files}개까지 가능합니다.')
            return redirect('inquiry')
        
        total_size = 0
        validated_attachments = []
        for file in attachments:
            # 파일 확장자 확인
            file_ext = os.path.splitext(file.name)[1].lower()
            if file_ext not in allowed_extensions:
                messages.error(request, f'{file.name}: 허용되지 않는 파일 형식입니다.')
                return redirect('inquiry')
            
            # 파일 크기 확인
            if file.size > max_file_size:
                messages.error(request, f'{file.name}: 파일 크기가 10MB를 초과합니다.')
                return redirect('inquiry')
            
            total_size += file.size
            
            # 파일 포인터를 처음으로 되돌림 (검증 과정에서 읽었을 수 있음)
            file.seek(0)
            
            # 파일 정보 저장 (원본 파일 객체를 직접 사용)
            validated_attachments.append({
                'name': file.name,
                'file': file,  # 원본 파일 객체 저장
                'content_type': file.content_type or 'application/octet-stream',
                'size': file.size
            })
        
        if total_size > max_total_size:
            messages.error(request, '총 파일 크기가 20MB를 초과합니다.')
            return redirect('inquiry')
        
        # 이메일 내용 구성
        subject = f'[견적문의] {company_name} - {product_name}'
        message = f'''견적문의가 접수되었습니다.

회사명: {company_name}
제품명: {product_name}
사이즈(형태): {size}
수량: {quantity}
기타 요청사항: {other_requests or '(없음)'}
'''
        
        if validated_attachments:
            message += f'\n첨부파일: {len(validated_attachments)}개\n'
            for att in validated_attachments:
                message += f'  - {att["name"]} ({att["size"] / 1024 / 1024:.2f}MB)\n'
        
        try:
            if not getattr(settings, 'EMAIL_HOST_USER', '').strip():
                raise ValueError('이메일 발신 계정이 설정되지 않았습니다.')
            if not getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip():
                raise ValueError('이메일 발신 비밀번호가 설정되지 않았습니다.')

            email = _build_inquiry_email(subject, message, validated_attachments)
            email.send(fail_silently=False)
        except Exception:
            logger.exception('견적문의 이메일 전송 실패')
            messages.error(
                request,
                '견적문의 이메일 전송에 실패했습니다. 이메일 설정을 확인한 뒤 다시 시도해주세요.',
            )
            return redirect('inquiry')

        messages.success(request, '견적문의가 성공적으로 전송되었습니다.')
        return redirect('inquiry')
    
    return render(request, 'main/inquiry.html')
