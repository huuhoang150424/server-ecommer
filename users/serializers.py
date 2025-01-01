from rest_framework  import serializers
from django.contrib.auth.hashers import make_password,check_password
from .models import Users
from django.forms.models import model_to_dict
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.conf import settings

from django_redis import get_redis_connection

class RegisterSerializers(serializers.ModelSerializer):
    password=serializers.CharField(max_length=50,write_only=True)
    confirmPassword=serializers.CharField(max_length=50,write_only=True)

    class Meta:
        model=Users
        fields=['name','password','email','confirmPassword']

    def create(self,data):
        data.pop('confirmPassword')
        data['password']=make_password(data['password'])
        newUser=Users.objects.create(**data)
        return newUser

    def validate(self,validated_data):
        if validated_data['password']!=validated_data['confirmPassword']:
            raise serializers.ValidationError('Xác nhận mật khẩu không chính xác')
        if Users.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError('Tài khoản đã tồn tại ')
        return validated_data


class LoginSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254) 
    password = serializers.CharField(max_length=50)
    class Meta:
        model = Users
        fields = ['password', 'email']

    def validate(self, validated_data):
        findUser = Users.objects.filter(email=validated_data['email']).first()
        if not findUser:
            raise serializers.ValidationError('Tài khoản không tồn tại')
        if not check_password(validated_data['password'], findUser.password):
            raise serializers.ValidationError('Mật khẩu không đúng')
        return findUser

class RefreshTokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254) 
    password = serializers.CharField(max_length=15)
    class Meta:
        model = Users
        fields = ['password', 'email']

    def validate(self, validated_data):
        findUser = Users.objects.filter(email=validated_data['email']).first()
        if not findUser:
            raise serializers.ValidationError('Tài khoản không tồn tại')
        if not check_password(validated_data['password'], findUser.password):
            raise serializers.ValidationError('Mật khẩu không đúng')
        return findUser

class LoginWithGoogleSeriaLizer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254) 
    password = serializers.CharField(max_length=15)
    class Meta:
        model = Users
        fields = ['password', 'email']

    def validate(self, validated_data):
        findUser = Users.objects.filter(email=validated_data['email']).first()
        if not findUser:
            raise serializers.ValidationError('Tài khoản không tồn tại')
        if not check_password(validated_data['password'], findUser.password):
            raise serializers.ValidationError('Mật khẩu không đúng')
        return findUser

class getAllUserSeriaLizer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id','name', 'email','gender','avatar','isAdmin','address']


class getUserSeriaLizer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id','name', 'email','gender','avatar','isAdmin','address','phone','birth_date']

class createUserSeriaLizer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50) 
    password = serializers.CharField(max_length=100, write_only=True)
    name = serializers.CharField(max_length=20)
    gender = serializers.ChoiceField(choices=Users._meta.get_field('gender').choices)
    avatar = serializers.CharField(max_length=150)

    class Meta:
        model = Users
        fields = ['name', 'email', 'gender', 'avatar', 'isAdmin', 'password']

    def create(self, data):
        user = Users(
            name=data['name'],
            email=data['email'],
            gender=data['gender'],
            avatar=data.get('avatar', Users._meta.get_field('avatar').default),  
            isAdmin=data.get('isAdmin', False)
        )
        user.password = make_password(data['password'])
        user.save()
        return user

    def validate(self, data):
        if Users.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('Email đã được đăng ký')
        if Users.objects.filter(name=data['name']).exists():
            raise serializers.ValidationError('Người dùng đã tồn tại')
        return data

class updateUserSeriaLizer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50) 
    name = serializers.CharField(max_length=20)
    gender = serializers.ChoiceField(choices=Users._meta.get_field('gender').choices)
    avatar = serializers.CharField(max_length=150)

    class Meta:
        model = Users
        fields = ['name', 'email', 'gender', 'avatar', 'isAdmin']

    def validate(self, data):
        id=self.context.get('id')
        if not Users.objects.filter(id=id).exists():
            raise serializers.ValidationError('Người dùng không tồn tại')
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50)
    name = serializers.CharField(max_length=20)
    gender = serializers.ChoiceField(choices=Users._meta.get_field('gender').choices)
    avatar = serializers.CharField(max_length=150)
    birth_date=serializers.DateField()
    class Meta:
        model = Users
        fields = ['name', 'email', 'gender', 'avatar', 'birth_date']





class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    def validate(self, data):
        email = data.get('email')
        if not Users.objects.filter(email=email).exists():
            raise serializers.ValidationError('Người dùng không tồn tại.')
        return data
    def save(self):
        email = self.validated_data['email']
        user = Users.objects.get(email=email)
        otp_code = get_random_string(length=4, allowed_chars='0123456789')

        redis_conn = get_redis_connection("default")
        redis_conn.setex(f"otp:{email}", 300, otp_code)

        # Lấy thời gian hết hạn còn lại của OTP từ Redis
        ttl = redis_conn.ttl(f"otp:{email}")
        if ttl > 0:
            expiration_time = now() + timedelta(seconds=ttl)
        else:
            expiration_time = None  # Nếu TTL không còn, có thể do OTP đã hết hạn và bị xóa
        send_mail(
            subject="Mã xác thực (OTP)",
            message=f"Chào {user.name},\n\nMã xác thực của bạn là: {otp_code}\nMã có hiệu lực trong 5 phút.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return {
            "message": "Mã OTP đã được gửi qua email.",
            "expiration": expiration_time,
            "email": email
        }

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp_code')
        redis_conn = get_redis_connection("default")
        stored_otp = redis_conn.get(f"otp:{email}")
        if stored_otp is None:
            raise serializers.ValidationError('Mã OTP đã hết hạn hoặc không tồn tại.')
        if stored_otp.decode() != otp_code:
            raise serializers.ValidationError('Mã OTP không hợp lệ.')
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            raise serializers.ValidationError('Email không tồn tại trong hệ thống.')
        self.user = user
        return data
    def save(self):
        # Sau khi xác thực thành công, xóa OTP khỏi Redis
        redis_conn = get_redis_connection("default")
        redis_conn.delete(f"otp:{self.user.email}")


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=50, write_only=True)
    confirmPassword = serializers.CharField(max_length=50, write_only=True)

    def validate(self, data):
        user = Users.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError("Tài khoản không tồn tại")
        if data['password'] != data['confirmPassword']:
            raise serializers.ValidationError("Xác nhận mật khẩu không chính xác")
        return data

    def save(self): 
        data = self.validated_data
        user = Users.objects.get(email=data['email'])
        user.password = make_password(data['password'])
        user.save()
        return user
