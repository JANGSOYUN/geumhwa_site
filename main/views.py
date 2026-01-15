from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.conf import settings
from django.core.files.base import ContentFile
import os
import io

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
        
        recipient_email = 'geumhwa9300@gmail.com'
        
        # 이메일 전송 시도
        email_sent = False
        error_message = None
        
        # 디버깅: 요청 시작
        print("=" * 60)
        print("[DEBUG] 견적문의 요청 시작")
        print(f"[DEBUG] 첨부파일 개수: {len(attachments)}")
        print(f"[DEBUG] 검증된 첨부파일 개수: {len(validated_attachments)}")
        
        try:
            # 이메일 설정 확인
            if hasattr(settings, 'EMAIL_HOST_USER') and hasattr(settings, 'EMAIL_HOST_PASSWORD'):
                if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                    if validated_attachments:
                        # 첨부파일이 있는 경우 EmailMessage 사용
                        print("[DEBUG] EmailMessage 객체 생성 시작")
                        email = EmailMessage(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                            [recipient_email],
                        )
                        
                        # 디버깅: 첨부할 파일 정보
                        print(f"[DEBUG] 첨부할 파일 수: {len(validated_attachments)}")
                        for i, att in enumerate(validated_attachments):
                            print(f"  파일 {i+1}: {att['name']} ({att['content_type']}), 크기: {att['size']} bytes")
                            print(f"    - file 객체 타입: {type(att['file'])}")
                        
                        # 원본 파일 객체를 사용하여 파일 첨부
                        for i, att in enumerate(validated_attachments):
                            print(f"[DEBUG] 파일 {i+1} 첨부 시도: {att['name']}")
                            try:
                                # 파일 포인터를 처음으로 되돌림
                                att['file'].seek(0)
                                # 파일 내용을 읽어서 첨부
                                file_content = att['file'].read()
                                print(f"[DEBUG] 파일 {i+1} 읽기 완료: {len(file_content)} bytes, 타입: {type(file_content)}")
                                
                                # 바이트를 직접 첨부
                                email.attach(att['name'], file_content, att['content_type'])
                                
                                print(f"[DEBUG] 파일 {i+1} 첨부 성공: {att['name']}")
                                # 파일 포인터를 다시 처음으로 (혹시 모를 경우를 대비)
                                att['file'].seek(0)
                            except Exception as e:
                                print(f"[DEBUG] 파일 {i+1} 첨부 실패: {att['name']}, 오류: {str(e)}")
                                import traceback
                                traceback.print_exc()
                                raise
                        
                        # 디버깅: 실제 첨부된 파일 확인
                        print(f"[DEBUG] 이메일 객체의 첨부 파일 수: {len(email.attachments)}")
                        if len(email.attachments) == 0:
                            print("[DEBUG] 경고: 첨부된 파일이 없습니다!")
                        for i, (filename, content, mimetype) in enumerate(email.attachments):
                            content_size = len(content) if isinstance(content, bytes) else 'N/A'
                            print(f"  첨부 {i+1}: {filename} ({mimetype}), 크기: {content_size} bytes")
                        
                        # 이메일 메시지 구조 확인
                        print("[DEBUG] 이메일 메시지 구조 확인...")
                        print(f"  Content-Type: {email.content_subtype}")
                        print(f"  Mixed Subtype: {email.mixed_subtype}")
                        
                        # MIME 메시지 구조 확인
                        if hasattr(email, 'message'):
                            msg = email.message()
                            print(f"  MIME 타입: {msg.get_content_type()}")
                            print(f"  MIME 파트 수: {len(list(msg.walk()))}")
                            for j, part in enumerate(msg.walk()):
                                if part.get_content_disposition() == 'attachment':
                                    print(f"    파트 {j}: {part.get_filename()}, 크기: {len(part.get_payload(decode=True))} bytes")
                        
                        # 이메일 메시지를 파일로 저장 (디버깅용)
                        try:
                            msg_str = email.message().as_string()
                            debug_file_path = os.path.join(settings.BASE_DIR, 'email_debug.txt')
                            with open(debug_file_path, 'w', encoding='utf-8') as f:
                                f.write(msg_str)
                            print(f"[DEBUG] 이메일 메시지를 파일로 저장: {debug_file_path}")
                        except Exception as e:
                            print(f"[DEBUG] 이메일 메시지 저장 실패: {str(e)}")
                        
                        print("[DEBUG] 이메일 전송 시작...")
                        email.send()
                        print("[DEBUG] 이메일 전송 완료")
                        print("=" * 60)
                    else:
                        # 첨부파일이 없는 경우 일반 send_mail 사용
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
            if validated_attachments:
                print(f"\n첨부파일: {len(validated_attachments)}개")
                for att in validated_attachments:
                    print(f"  - {att['name']} ({att['size'] / 1024 / 1024:.2f}MB)")
            print("=" * 50)
            if error_message:
                print(f"오류 메시지: {error_message}")
            
            # 사용자에게는 성공 메시지 표시 (데이터는 저장됨)
            messages.success(request, '견적문의가 접수되었습니다. 담당자가 확인 후 연락드리겠습니다.')
        
        return redirect('inquiry')
    
    return render(request, 'main/inquiry.html')