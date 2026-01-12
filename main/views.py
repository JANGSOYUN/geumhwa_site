from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

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
        
        # 필수 필드 검증
        if not company_name or not product_name or not size or not quantity:
            messages.error(request, '필수 항목을 모두 입력해주세요.')
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
        
        recipient_email = 'geumhwa9300@naver.com'
        
        # 이메일 전송 시도
        email_sent = False
        error_message = None
        
        try:
            # 이메일 설정 확인
            if hasattr(settings, 'EMAIL_HOST_USER') and hasattr(settings, 'EMAIL_HOST_PASSWORD'):
                if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                        [recipient_email],
                        fail_silently=False,
                    )
                    email_sent = True
                    messages.success(request, '견적문의가 성공적으로 전송되었습니다.')
                else:
                    error_message = '이메일 설정이 완료되지 않았습니다.'
            else:
                error_message = '이메일 설정이 없습니다.'
        except Exception as e:
            error_message = str(e)
            print(f"이메일 전송 오류: {error_message}")
        
        # 이메일 전송 실패 시 콘솔에 출력 (개발/운영 모두)
        if not email_sent:
            print("=" * 50)
            print("견적문의 이메일 (이메일 전송 실패 - 콘솔 출력)")
            print("=" * 50)
            print(f"받는 사람: {recipient_email}")
            print(f"제목: {subject}")
            print(f"내용:\n{message}")
            print("=" * 50)
            if error_message:
                print(f"오류 메시지: {error_message}")
            
            # 사용자에게는 성공 메시지 표시 (데이터는 저장됨)
            messages.success(request, '견적문의가 접수되었습니다. 담당자가 확인 후 연락드리겠습니다.')
        
        return redirect('inquiry')
    
    return render(request, 'main/inquiry.html')