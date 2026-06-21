from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMessage


class DynamicEmailService:
    SMTP_CONFIGS = {
        'gmail.com': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True
        },
        'outlook.com': {
            'host': 'smtp.office365.com',
            'port': 587,
            'use_tls': True
        },
        'hotmail.com': {
            'host': 'smtp.office365.com',
            'port': 587,
            'use_tls': True
        },
        'office365.com': {
            'host': 'smtp.office365.com',
            'port': 587,
            'use_tls': True
        },
        'lavergne.ca': {
            'host': 'smtp.office365.com',
            'port': 587,
            'use_tls': True
        }
    }

    @classmethod
    def get_smtp_backend(cls, email: str, password: str) -> EmailBackend:
        try:
            domain = email.split('@')[1].lower()
        except IndexError:
            raise ValueError("Email Format is not correct")

        config = cls.SMTP_CONFIGS.get(domain)
        if not config:
            config = {
                'host': 'smtp.office365.com',
                'port': 587,
                'use_tls': True
            }

        return EmailBackend(
            host=config['host'],
            port=config['port'],
            username=email,
            password=password,
            use_tls=config['use_tls'],
            fail_silently=False
        )

    @classmethod
    def send_report(cls, sender_email, sender_password, recipients, subject, body, pdf_file=None):
        """
        Xử lý kết nối và thực hiện gửi Email
        """
        backend = cls.get_smtp_backend(sender_email, sender_password)
        email_msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=sender_email,
            to=recipients,
            connection=backend
        )

        if pdf_file:
            email_msg.attach(pdf_file.name, pdf_file.read(), pdf_file.content_type)
        email_msg.send()
