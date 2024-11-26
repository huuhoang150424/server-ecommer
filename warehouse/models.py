from django.db import models
from product.models import ProductModel
import uuid;


class WarehouseStatusChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Hoạt động'
    INACTIVE = 'INACTIVE', 'Ngừng hoạt động'
    FULL = 'FULL', 'Đầy'
    EMPTY = 'EMPTY', 'Trống'
    UNDER_MAINTENANCE = 'UNDER_MAINTENANCE', 'Đang bảo trì'


class Warehouse(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    warehouse_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.IntegerField()
    status = models.CharField(
        max_length=50,
        choices=WarehouseStatusChoices.choices,
        default=WarehouseStatusChoices.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.warehouse_name

    class Meta:
        db_table = 'warehouse'

class WarehouseProduct(models.Model):
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE,  
        related_name='warehouse'  
    )
    # product = models.ForeignKey(
    #     ProductModel, 
    #     on_delete=models.CASCADE,  
    #     related_name='products' 
    # )
    quantity = models.IntegerField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.warehouse_name
    class Meta:
        db_table='warehouse_product'