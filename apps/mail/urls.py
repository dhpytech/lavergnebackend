from django.urls import path,include
from rest_framework.routers import DefaultRouter
from mail.views import MailViewSet, send_report_email_view

router = DefaultRouter()
router.register('mail', MailViewSet, basename='mail')

urlpatterns = [
    path('send-report-email/', send_report_email_view, name='send-report-email'),
    path('', include(router.urls)),
 ]
