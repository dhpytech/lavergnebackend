from django.urls import path
from .views import RegisterView, CustomLoginView, RefreshTokenView, LogoutView, HomeView
from .views import TenNhanVienListCreateAPIView
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('token/login/', CustomLoginView.as_view()),
    path('token/refresh/', RefreshTokenView.as_view()),
    path('token/logout/', LogoutView.as_view()),
    path('home/', HomeView.as_view()),
    path('nhanvien/', TenNhanVienListCreateAPIView.as_view()),
]
