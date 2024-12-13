from django.db import models
import uuid
from users.models import Users
from product.models import ProductModel


class statusModel(models.TextChoices):
    CONFIRMED = 'Xác nhận'
    NOT_CONFIRMED = 'Chưa xác nhận'

class orderModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    user = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='orders'  
    ) 
    total_amount=models.FloatField()
    status=models.CharField(
        max_length=20,
        choices=statusModel.choices,
        default=statusModel.NOT_CONFIRMED
    )
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    class Meta:
        db_table='orders'


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
        related_name='order_detail'  
    ) 
    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.CASCADE, 
        related_name='order_detail'  
    ) 

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    class Meta:
        db_table='order_detail'