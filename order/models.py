from django.db import models
import uuid
from users.models import Users
from product.models import ProductModel
import random

class statusOrderModel(models.TextChoices):
    CONFIRMED = 'CONFIRMED','Xác nhận'
    NOT_CONFIRMED = 'NOT_CONFIRMED','Chưa xác nhận'

class orderModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    order_code = models.CharField(
        max_length=7, 
        unique=True, 
        editable=False,
        blank=True
    )
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total_amount = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=statusOrderModel.choices,
        default=statusOrderModel.NOT_CONFIRMED
    )
    shipping_address = models.TextField(null=True,blank=True)  
    receiver_name = models.CharField(max_length=255,null=True,blank=True)  
    receiver_phone = models.CharField(max_length=15,null=True,blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self.generate_order_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_code():
        while True:
            code = f"A{random.randint(100000, 999999)}"  # Sinh mã dạng Axxxxx
            if not orderModel.objects.filter(order_code=code).exists():
                return code

    def __str__(self):
        return f'{self.order_code} {self.total_amount}'



class orderDetailModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    price=models.FloatField()
    quantity=models.IntegerField()
    order = models.ForeignKey(
        orderModel, 
        on_delete=models.CASCADE, 
        related_name='order_details'  
    ) 
    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.CASCADE, 
        related_name='order_products'  
    ) 

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    class Meta:
        db_table='order_detail'
    def __str__(self):
        return f"{self.id} {self.price}"

class StatusModel(models.TextChoices):
    PROCESSING = 'PROCESSING', 'Đang xử lý'
    SHIPPED = 'SHIPPED', 'Đã giao'
    DELIVERED = 'DELIVERED', 'Đã giao hàng'
    CANCELLED = 'CANCELLED', 'Hủy'
class orderHistoryModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    status = models.CharField(
        max_length=20,
        choices=StatusModel.choices,
        default=StatusModel.PROCESSING
    )
    order = models.ForeignKey(
        orderModel,
        on_delete=models.CASCADE,
        related_name='order_histories' 
    )
    change_by = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='order_histories'
    )
    changed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_history'


    def __str__(self):
        return f"{self.id} {self.status} {self.order}"
    