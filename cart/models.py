from django.db import models
import uuid
from users.models import Users
from product.models import ProductModel




class cartModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    user = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='carts'  # Danh sách giỏ hàng của người dùng
    )    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart {self.id} for User {self.user.id}"



class cartItemModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,  
        default=uuid.uuid4
    )
    cart = models.ForeignKey(
        cartModel,
        on_delete=models.CASCADE, 
        related_name='cart_items'
    )
    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)  
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = 'cart_items'

    def __str__(self):
        return f"CartItem {self.id} in Cart {self.cart.id}"
