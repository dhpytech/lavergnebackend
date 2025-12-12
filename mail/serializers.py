from rest_framework import serializers
from mail.models import Mail


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ['mail_address', 'mail_person', 'mail_status']
