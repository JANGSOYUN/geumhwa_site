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

def box_products(request):
    return render(request, 'main/box_products.html')

def equipment(request):
    return render(request, 'main/equipment.html')

def inquiry(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name', '')
        product_name = request.POST.get('product_name', '')
        size = request.POST.get('size', '')
        quantity = request.POST.get('quantity', '')
        other_requests = request.POST.get('other_requests', '')
        
        # 이메일 내용 구성
        subject = f'[견적문의] {company_name} - {product_name}'
        message = f'''견적문의가 접수되었습니다.

회사명: {company_name}
제품명: {product_name}
사이즈(형태): {size}
수량: {quantity}
기타 요청사항: {other_requests}
'''
        
        recipient_email = 'jangwkd@gmail.com'  # 테스트용
        
        try:
            # 이메일 전송 시도
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                    [recipient_email],
                    fail_silently=False,
                )
                messages.success(request, '견적문의가 성공적으로 전송되었습니다.')
            else:
                # 이메일 설정이 없으면 콘솔에 출력 (개발 환경)
                print("=" * 50)
                print("견적문의 이메일 (개발 모드 - 실제 전송되지 않음)")
                print("=" * 50)
                print(f"받는 사람: {recipient_email}")
                print(f"제목: {subject}")
                print(f"내용:\n{message}")
                print("=" * 50)
                messages.success(request, '견적문의가 접수되었습니다. (개발 모드)')
        except Exception as e:
            print(f"이메일 전송 오류: {str(e)}")
            messages.error(request, '이메일 전송 중 오류가 발생했습니다. 관리자에게 문의해주세요.')
        
        return redirect('inquiry')
    
    return render(request, 'main/inquiry.html')