from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarisInputViewSet, MetalInputViewSet, BaggingInputViewSet, IsoMonthlyViewSet

# Sử dụng DefaultRouter để tự động hóa các endpoint (GET, POST, PUT, DELETE)
router = DefaultRouter()

router.register(r'maris', MarisInputViewSet, basename='maris')
router.register(r'metal', MetalInputViewSet, basename='metal')
router.register(r'bagging', BaggingInputViewSet, basename='bagging')
router.register(r'iso-file', IsoMonthlyViewSet, basename='iso-file')

# Kết nối router vào urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]
