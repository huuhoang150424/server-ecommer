from rest_framework  import serializers
from django.contrib.auth.hashers import make_password,check_password
from .models import Users
from django.forms.models import model_to_dict



class RegisterSerializers(serializers.ModelSerializer):
    password=serializers.CharField(max_length=15,write_only=True)
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