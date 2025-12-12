from django.urls import path,include
from rest_framework.routers import DefaultRouter
from mail.views import MailViewSet

router = DefaultRouter()
router.register('mail', MailViewSet, basename='mail')

urlpatterns = [
    path('', include(router.urls)),
]