from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SafetyTimeViewSet
from .views import SafetyDurationView

router = DefaultRouter()
router.register(r'safety-time', SafetyTimeViewSet, basename='safety-time')

urlpatterns = [
    path('', include(router.urls)),
    path('duration/', SafetyDurationView.as_view(), name='safety-duration-view'),
]
