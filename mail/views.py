from django.shortcuts import render
from rest_framework import viewsets
from mail.models import Mail
from mail.serializers import MailSerializer


# Create your views here.
class MailViewSet(viewsets.ModelViewSet):
    queryset = Mail.object.all().order_by('-mail_address')
    serializer_class = MailSerializer
