from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from .utils import generaToken
from .models import Users
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from utils.pagination import CustomPagination
from .decorator import admin_required,user_required
from utils.response import SuccessResponse,ErrorResponse
from django.db.models import Count
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings


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
                    'avatar': user.avatar,
                    'address': user.address,
                    'birth_date': user.birth_date,
                    'gender': user.gender,
                    'phone': user.phone,
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
    response= Response({ 'message': 'Đăng xuất thành công'}, status=status.HTTP_200_OK)
    response.delete_cookie('refreshToken')
    return response

@api_view(['GET'])
def refreshToken(request):
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
    try: 
        pass
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def verifyCode(request):
    try:
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return SuccessResponse({"message": "Mã OTP hợp lệ và đã được xác thực."}, status=status.HTTP_200_OK)
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ErrorResponse(
            {"error_message": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def forgotPassword(request):
    try:
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return SuccessResponse({
                'message': 'Gửi mail thành công',
                'data': result
            }, status=status.HTTP_200_OK)
        return ErrorResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ErrorResponse(
            {"error_message": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PATCH'])
@user_required 
def changePassword(request):
    try:
        old_password = request.data.get('oldPassword')
        new_password = request.data.get('newPassword')
        confirm_password = request.data.get('confirmPassword')
        user_id=request.user.id
        user = Users.objects.get(id=user_id)

        if not check_password(old_password, user.password):
            return ErrorResponse(error_message="Mật khẩu cũ không đúng", status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return ErrorResponse(error_message="Mật khẩu xác nhận không khớp", status=status.HTTP_400_BAD_REQUEST)
        user.password = make_password(new_password)
        user.save()
        return Response({"message": "Mật khẩu đã được thay đổi thành công!"}, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return ErrorResponse(error_message="Tài khoản không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@user_required 
def changePhone(request):
    try:
        phone = request.data.get('phone')
        user_id=request.user.id
        user = Users.objects.get(id=user_id)
        user.phone =phone
        user.save()
        return SuccessResponse({"message": "Số điện thoại đã được thay đổi thành công!"}, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return ErrorResponse(error_message="Người dùng không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def resetPassword(request):
    try: 
        resetPassword_serializer=ResetPasswordSerializer(
            data=request.data
        )
        if resetPassword_serializer.is_valid():
            resetPassword_serializer.save()
            return SuccessResponse({
                'message': 'Đổi mật khẩu thành công'
            },status=status.HTTP_200_OK )
        
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@admin_required
def getAllUser(request):
    try:
        allUsers = Users.objects.all().order_by('id')
        paginator = CustomPagination()
        paginated_data = paginator.paginate_queryset(allUsers, request)
        if paginated_data is None:  
            user_serializer = getAllUserSeriaLizer(allUsers, many=True)
            return SuccessResponse({
                'totalItems': len(allUsers),
                'currentPage': 1,
                'totalPages': 1,
                'pageSize': len(allUsers),
                'data': user_serializer.data
            },status=status.HTTP_200_OK)
        user_serializer = getAllUserSeriaLizer(paginated_data, many=True)

        return paginator.get_pagination_response(user_serializer.data)

    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@user_required
def createUser(request):
    try: 
        createUserSeriaLizers=createUserSeriaLizer(data=request.data)
        if createUserSeriaLizers.is_valid():
            createUserSeriaLizers.save()
            return SuccessResponse(
                {'message': 'Tạo mới người dùng thành công'}, 
                status=status.HTTP_201_CREATED
            )
        return ErrorResponse(
            error_message=createUserSeriaLizers.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@user_required
def getUser(request):
    try:
        user_id=request.user.id
        user = Users.objects.get(id=user_id)
        serializers=getUserSeriaLizer(user)

        return SuccessResponse(
            {'message': 'Thành công','data': serializers.data}, 
            status=status.HTTP_200_OK
        )

    except Users.DoesNotExist:
        return ErrorResponse(error_message="Tài khoản không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['DELETE'])
@admin_required
def deleteUser(request,id):
    try: 
        if Users.objects.filter(id=id,isAdmin=True).exists():
            return ErrorResponse(
                {'message': 'Không thể xóa Admin'},
                status=status.HTTP_404_NOT_FOUND
            )
        user=Users.objects.filter(id=id)
        user.delete()
        return SuccessResponse({
            'message': 'Xóa người dùng thàng công'
        },status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return ErrorResponse(error_message="Người dùng không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@admin_required
def updateUser(request,id):
    try: 
        user=Users.objects.get(id=id)
        serializer=updateUserSeriaLizer(
            instance=user,
            data=request.data,
            context={
                'id': id
            }
        )
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse({
                'message': 'Cập nhật người dùng thành công'
            },status=status.HTTP_200_OK )
        return ErrorResponse({
            'message': 'Dữ liệu không hợp lệ',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Users.DoesNotExist:
        return ErrorResponse(error_message="Người dùng không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
@user_required
def updateProfile(request):
    try:
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        serializer = UpdateProfileSerializer(
            instance=user,
            data=request.data,
            partial=True  # Cho phép cập nhật một phần thông tin
        )
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse({
                'message': 'Cập nhật thông tin người dùng thành công',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return ErrorResponse({
            'message': 'Dữ liệu không hợp lệ',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Users.DoesNotExist:
        return ErrorResponse(error_message="Người dùng không tồn tại", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ErrorResponse(error_message=str(e),  status=status.HTTP_500_INTERNAL_SERVER_ERROR )

@api_view(['PATCH'])
@user_required
def addAddress(request):
    try:
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        address = request.data.get("address")
        
        if not address:
            return ErrorResponse(
                error_message="Địa chỉ không được để trống", 
                status=status.HTTP_400_BAD_REQUEST
            )
        if address in user.address:
            return ErrorResponse(
                error_message="Địa chỉ này đã tồn tại", 
                status=status.HTTP_400_BAD_REQUEST
            )
        user.address.append(address)
        user.save()
        
        return SuccessResponse({
            'message': 'Thêm mới địa chỉ thành công',
            'updated_address_list': user.address
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(
            error_message=str(e), 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PATCH'])
@user_required
def deleteAddress(request):
    try:
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        addressRemove = request.data.get("address")
        if not addressRemove:
            return ErrorResponse(
                error_message="Địa chỉ cần xóa không được để trống", 
                status=status.HTTP_400_BAD_REQUEST
            )
        if addressRemove not in user.address:
            return ErrorResponse(
                error_message="Địa chỉ không tồn tại trong danh sách", 
                status=status.HTTP_400_BAD_REQUEST
            )
        user.address.remove(addressRemove)
        user.save()
        return SuccessResponse({
            'message': 'Xóa địa chỉ thành công',
            'updated_address_list': user.address
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(
            error_message=str(e), 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required
def getUserBuyProductSoMuch(request):
    try:
        users = Users.objects.annotate(order_count=Count('orders')).order_by('-order_count')[:20]
        serializer = GetUserBuyProductSoMuchSerializer(users, many=True)
        return SuccessResponse({
            'message': 'Thành công',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return ErrorResponse(
            error_message=str(e), 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
