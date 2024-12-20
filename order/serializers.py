from rest_framework  import serializers
from .models import orderDetailModel,orderModel
from users.serializers import getUserSeriaLizer
from product.models import ProductModel
from category.serializers import GetCatSerializer



class ProductSerializer(serializers.ModelSerializer):
    category=GetCatSerializer(read_only=True)

    class Meta:
        model = ProductModel
        fields = ['product_name', 'price', 'thumb_image','stock','category']

class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  
    class Meta:
        model = orderDetailModel
        fields = ['id','product', 'quantity', 'price']



class OrderSerializer(serializers.ModelSerializer):
    user=serializers.SerializerMethodField()
    class Meta:
        model = orderModel
        fields = ['id', 'user', 'total_amount', 'status', 'created_at', 'shipping_address','receiver_name','receiver_phone','order_code']
    def get_user(self, obj):
        if obj.user:
            return {
                'name': obj.user.name,
                'email': obj.user.email
            }
        return None

class OrderByUserSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True) 
    class Meta:
        model = orderModel
        fields = ['id', 'total_amount', 'status', 'created_at', 'order_details','shipping_address','receiver_name','receiver_phone']
    def get_order_details(self, obj):
        return obj