from rest_framework import serializers
from .models import cartItemModel,cartModel
from product.serializers import getProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product=getProductSerializer(read_only=True)
    class Meta:
        model = cartItemModel
        fields = ["id", "product", "quantity"]

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)


    class Meta:
        model = cartModel
        fields = ["id", "user", "cart_items"]

