from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import ListCreateAPIView
from .models import TenNhanVien
from .serializers import TenNhanVienSerializer

# REGISTER
class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# LOGIN
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


class CustomLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data.get('access')
        refresh_token = response.data.get('refresh')

        if access_token and refresh_token:
            res = Response({'access': access_token}, status=status.HTTP_200_OK)
            res.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                path='/api/token/refresh/'
            )
            return res
        return Response({'error': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)


# REFRESH TOKEN API
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            raise AuthenticationFailed('No refresh token')

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access': access_token})
        except Exception:
            raise AuthenticationFailed('Invalid refresh token')


# LOGOUT API
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()

            res = Response({'detail': 'Logged out'}, status=status.HTTP_200_OK)
            res.delete_cookie('refresh_token')
            return res
        except Exception as e:
            return Response({'detail': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)


# HOME API
class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Chào {request.user.username}!"})


class TenNhanVienListCreateAPIView(ListCreateAPIView):
    queryset = TenNhanVien.objects.all()
    serializer_class = TenNhanVienSerializer
