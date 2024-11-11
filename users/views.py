from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .serializers import RegisterSerializers,LoginSerializers,LoginWithGoogleSeriaLizer,RefreshTokenSerializer
from .utils import generaToken
from .models import Users
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

@api_view(['POST'])
def register(request):
    register_serializers=RegisterSerializers(data=request.data)
    if register_serializers.is_valid():
        register_serializers.save()
        return Response(
            {'message': 'Đăng ký thành công'}, 
            status=status.HTTP_201_CREATED
        )
    return Response(
        {'errors': register_serializers.errors, 'message': 'Đăng ký thất bại'}, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        login_serializer = LoginSerializers(data=request.data)
        if login_serializer.is_valid():
            user = login_serializer.validated_data 
            token = generaToken(user)
            response = Response(
                {
                    'message': 'Đăng nhập thành công',
                    'user': {
                        'id': str(user.id),
                        'name': user.name,
                        'email': user.email,
                        'avatar': user.avatar
                    },
                    'accessToken': token['accessToken']
                },
                status=status.HTTP_200_OK
            )
            expiration = timezone.now() + timedelta(days=365)  #hạn 365 ngày
            response.set_cookie(
                key='refreshToken',
                value=token['refreshToken'],
                expires=expiration,
                httponly=True,  # Không cho phép JavaScript truy cập cookie này
                secure=True,    # Chỉ sử dụng cookie qua HTTPS
                samesite='Lax'  # chống CSRF
            )
            return response
        return Response(
            {'data': login_serializer.errors,'message': 'Đăng nhập thất bại'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def logout(request):
    response= Response({
        'message': 'Đăng xuất thành công'
    },
    status=status.HTTP_200_OK
    )
    response.delete_cookie('refreshToken')
    return response

@api_view(['GET'])
def refreshToken(request):
    if request.method=='GET':
        refresh_token=request.COOKIES.get('refreshToken')
        print(refresh_token)
        try:
            # Xác thực refresh token
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({
                'refreshToken': str(refresh),
                'accessToken': access_token
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Refresh token không hợp lệ'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def loginWithGoogle(request):
    pass