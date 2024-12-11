from django.db import models
from category.models import CategoryModel
import uuid
from users.models import Users
from django.utils.text import slugify


class StatusChoices(models.TextChoices):
    AVAILABLE =  'Có sẵn'
    OUT_OF_STOCK =  'Hết hàng'
    DISCONTINUED =  'Ngưng bán'


class ProductModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    slug = models.SlugField(
        max_length=60, 
        unique=True, 
        blank=True  # Để tự động tạo khi lưu
    )
    product_name = models.CharField(max_length=50)
    price = models.FloatField() 
    thumb_image = models.CharField(max_length=300)
    stock = models.IntegerField() 
    image_urls = models.JSONField()  
    description=models.TextField(default="")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.AVAILABLE
    )
    category = models.ForeignKey(
        CategoryModel, 
        on_delete=models.CASCADE,  # Hành động khi xóa category
        related_name='products'  # truy vấn con từ cat --> product
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.product_name)
            slug = base_slug
            counter = 1
            # Kiểm tra trùng lặp slug
            while ProductModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Tên sản phẩm: {self.product_name}   id: {self.id}"
    
    class Meta:
        db_table = 'products'

        
class AttributesModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    attribute_name = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return self.attribute_name
    class Meta:
        db_table = 'attributes'

class ProductAttributesModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    product = models.ForeignKey(
        'ProductModel',
        on_delete=models.CASCADE,
        related_name='product_attributes'
    )
    attribute = models.ForeignKey(
        AttributesModel, 
        on_delete=models.CASCADE,
        related_name='product_attributes'
    )
    value = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.product} - {self.attribute}: {self.value}"

    class Meta:
        db_table = 'product_attributes'





class FavoriteProductModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    user = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='favorite_product'  
    )
    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.CASCADE, 
        related_name='favorite_product'  
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f""
    
    class Meta:
        db_table = 'favorite_product'

