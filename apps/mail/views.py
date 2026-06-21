from django.shortcuts import render
from rest_framework import viewsets,status
from mail.models import Mail
from mail.serializers import MailSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
import logging

from .services.mail_services import DynamicEmailService

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json

logger = logging.getLogger(__name__)


class MailViewSet(viewsets.ModelViewSet):
    queryset = Mail.objects.all().order_by('-mail_person')
    serializer_class = MailSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def send_report_email_view(request):
    try:
        # Thu thập thông tin từ FormData
        sender_email = request.POST.get('sender_email')
        sender_password = request.POST.get('sender_password')
        subject = request.POST.get('subject')
        notes = request.POST.get('notes')

        # Đọc tham số danh sách người nhận
        recipients_json = request.POST.get('recipients')

        # SỬA LỖI CHÍ MẠNG: Kiểm tra và bọc lọc lỗi giải mã chuỗi JSON một cách độc lập
        if not recipients_json or recipients_json.strip() == "":
            return Response({
                'success': False,
                'message': 'Data processing error: Field "recipients" is completely empty or missing from request.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipients_list = json.loads(recipients_json)
        except json.JSONDecodeError as json_err:
            # Nếu chuỗi truyền lên không phải cấu trúc JSON (ví dụ chuỗi văn bản trơn), chặn đứng tại đây
            return Response({
                'success': False,
                'message': f'Data processing validation error: Received non-JSON string. Raw data payload: "{recipients_json}"'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra tính toàn vẹn sau khi parse thành công
        if not sender_email or not sender_password:
            return Response({
                'success': False,
                'message': 'Configuration profiles incomplete: Sender account or credentials missing.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(recipients_list, list) or len(recipients_list) == 0:
            return Response({
                'success': False,
                'message': 'Validation fail: Recipient index must be a list containing at least one target email address.'
            }, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return Response({
                'success': False,
                'message': 'Payload transfer failure: Attached report file stream was empty.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cấu hình nội dung email mặc định nếu không có ghi chú thêm
        body_content = notes if (notes and notes.strip()) else "Please find the attached Daily Production Report."

        # Chuyển tiếp luồng xử lý qua dịch vụ SMTP chuyên dụng của bạn
        DynamicEmailService.send_report(
            sender_email=sender_email,
            sender_password=sender_password,
            recipients=recipients_list,
            subject=subject if subject else "Daily Production Report",
            body=body_content,
            pdf_file=pdf_file
        )

        return Response({
            'success': True,
            'message': 'Report email successfully processed and sent.'
        }, status=status.HTTP_200_OK)

    except ValueError as val_err:
        return Response({
            'success': False,
            'message': f'Runtime parameter evaluation failure: {str(val_err)}'
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Mail view unexpected runtime crash: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': f'SMTP authentication or network pipe failure: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
