from django.db import models
import uuid
from order.models import orderModel
from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', 'Chờ xử lý'
    COMPLETED = 'Completed', 'Đã hoàn thành'
    FAILED = 'Failed', 'Thất bại'
    CANCELLED = 'Cancelled', 'Đã hủy'

class PaymentMethod(models.TextChoices):
    COD =  'Thanh toán trực tiếp'  
    MOMO = 'MOMO'
    PAYPAL = 'PayPal'

class PaymentModel(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        orderModel,  
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethod.choices, 
        default=PaymentMethod.COD
    )
    payment_status = models.CharField(
        max_length=50,
        choices=PaymentStatus.choices,  
        default=PaymentStatus.PENDING  
    )
    transaction_id = models.CharField(max_length=255) #mã giao dịch bên momo hoặc paypal
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'


