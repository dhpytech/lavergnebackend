from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarisInputViewSet, MetalInputViewSet, BaggingInputViewSet

# Sử dụng DefaultRouter để tự động hóa các endpoint (GET, POST, PUT, DELETE)
router = DefaultRouter()

# 1. Maris Entry
router.register(r'maris', MarisInputViewSet, basename='maris')

# 2. Metal Entry
router.register(r'metal', MetalInputViewSet, basename='metal')

# 3. Bagging Entry
router.register(r'bagging', BaggingInputViewSet, basename='bagging')

# Kết nối router vào urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]
