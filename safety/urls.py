from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SafetyTimeViewSet

router = DefaultRouter()
router.register(r'safety-time', SafetyTimeViewSet, basename='safety-time')

urlpatterns = [
    path('', include(router.urls)),
]
