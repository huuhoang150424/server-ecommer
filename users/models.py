from django.db import models
import uuid


class Gender(models.TextChoices):
    MALE = 'Male', 'Nam'
    FEMALE = 'Female', 'Nữ'
    OTHER = 'Other', 'Khác'

class Users(models.Model):
    id=models.UUIDField(
        primary_key=True,
        editable=True,
        default=uuid.uuid4
    )
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50) 
    password = models.CharField(max_length=100) 
    gender = models.CharField(
        max_length=20, 
        choices=Gender.choices, 
        default=Gender.OTHER
    )

    isAdmin = models.BooleanField(default=False, null=True)
    avatar = models.CharField(
        max_length=150, 
        default='https://res.cloudinary.com/dw3oj3iju/image/upload/v1709749732/chat_app/b1rj7epnhdqo6t7mcu5w.jpg'
    )
    address = models.TextField(  # Trường địa chỉ
        null=True, 
        blank=True, 
        default="Chưa cập nhật"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} {self.id} {self.email} {self.password} "
